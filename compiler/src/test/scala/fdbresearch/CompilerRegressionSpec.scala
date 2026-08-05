package fdbresearch

import fdbresearch.codegen.{CodeGenOptions, CppCodeGen}
import fdbresearch.parsing.{SQLParser, VariableOrderParser}
import fdbresearch.tree.VariableOrder
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.Assertions.intercept

import java.nio.file.{Path, Paths}
import scala.io.Source

class CompilerRegressionSpec extends AnyFunSuite {

  private val repoRoot: Path = Paths.get("").toAbsolutePath.getParent

  private def readFile(path: Path): String = {
    val source = Source.fromFile(path.toFile)
    try source.mkString
    finally source.close()
  }

  private def compileM3(relativeSqlPath: String): String = {
    compileTypedM3(relativeSqlPath).toString
  }

  private def compileTypedM3(relativeSqlPath: String): fdbresearch.core.M3.System = {
    val sqlPath = repoRoot.resolve(relativeSqlPath)
    val sql = new SQLParser().apply(readFile(sqlPath))
    val variableOrder =
      if (sql.variableOrder.isDefined) {
        val voPath = sqlPath.getParent.resolve(sql.variableOrder.get.file.path)
        new VariableOrderParser().apply(readFile(voPath))
      } else {
        VariableOrder.apply(sql)
      }

    new Driver().compile(sql, variableOrder, batchUpdates = true)
  }

  private def compileCpp(relativeSqlPath: String): String = {
    val opts =
      new CodeGenOptions("Query", "fdbresearch.gen", "standard", false, 0, true, false, 0L, true, true, true)
    new CppCodeGen(opts).apply(compileTypedM3(relativeSqlPath))
  }

  test("simple rst_RT query produces stable M3 triggers and maps") {
    val m3 = compileM3("examples/queries/simple/rst_RT.sql")

    assert(m3.contains("CREATE STREAM R (a int, b float)"))
    assert(m3.contains("DECLARE MAP V_A_RTS1(float)[][] :="))
    assert(m3.contains("DECLARE MAP V_E_S1(long)[][A: int, C: int] :="))
    assert(m3.contains("ON BATCH UPDATE OF R {"))
    assert(m3.contains("ON BATCH UPDATE OF T {"))
    assert(m3.contains("ON SYSTEM READY {"))
  }

  test("simple rst_RT query produces expected C++ relation and map definitions") {
    val cpp = compileCpp("examples/queries/simple/rst_RT.sql")

    assert(cpp.contains("#define RELATION_R_DYNAMIC"))
    assert(cpp.contains("#define RELATION_S_STATIC"))
    assert(cpp.contains("#define RELATION_T_DYNAMIC"))
    assert(cpp.contains("struct R_entry"))
    assert(cpp.contains("typedef MultiHashMap<V_B_R1_entry, float"))
    assert(cpp.contains("typedef MultiHashMap<V_E_S1_entry, int64_t"))
  }

  test("housing regression query produces stable ring-aware M3 artifacts") {
    val m3 = compileM3("examples/queries/housing/housing_regression.sql")

    assert(m3.contains("CREATE  TYPE RingCofactor"))
    assert(m3.contains("FROM FILE './datasets/housing-4-normalised/House.tbl'"))
    assert(m3.contains("DECLARE QUERY V_postcode_HSIRDT1 := V_postcode_HSIRDT1(RingCofactor<0, double, 27>)[][]<Local>;"))
    assert(m3.contains("ON BATCH UPDATE OF HOUSE {"))
    assert(m3.contains("ON BATCH UPDATE OF SHOP {"))
    assert(m3.contains("ON BATCH UPDATE OF INSTITUTION {"))
    assert(m3.contains("ON BATCH UPDATE OF RESTAURANT {"))
    assert(m3.contains("ON BATCH UPDATE OF DEMOGRAPHICS {"))
    assert(m3.contains("ON BATCH UPDATE OF TRANSPORT {"))
  }

  test("tpch query12 preserves grouped query output and predicate lowering") {
    val m3 = compileM3("examples/queries/tpch/tpch_query12.sql")

    assert(m3.contains("CREATE  TYPE RingPair FROM FILE 'ring/ring_pair.hpp';"))
    assert(m3.contains("DECLARE QUERY V_orderkey_LO1 := V_orderkey_LO1(RingPair)[][l_shipmode]<Local>;"))
    assert(m3.contains("{l_shipmode IN ['MAIL', 'SHIP']}"))
    assert(m3.contains("{l_commitdate < l_receiptdate}"))
    assert(m3.contains("{l_receiptdate >= [date: date]('1994-01-01')}"))
    assert(m3.contains("ON BATCH UPDATE OF LINEITEM {"))
    assert(m3.contains("ON BATCH UPDATE OF ORDERS {"))
  }

  test("simple datacube query preserves custom liftgroupby ring structure") {
    val m3 = compileM3("examples/queries/simple/rst_datacube.sql")

    assert(m3.contains("CREATE  TYPE DataCube"))
    assert(m3.contains("DECLARE QUERY V_A_RTS1 := V_A_RTS1(DataCube<[0, int, int, int]>)[][]<Local>;"))
    assert(m3.contains("[liftgroupby<0>: DataCube<[0, int]>](A)"))
    assert(m3.contains("[liftgroupby<1>: DataCube<[1, int]>](C)"))
    assert(m3.contains("[liftgroupby<2>: DataCube<[2, int]>](D)"))
    assert(m3.contains("ON BATCH UPDATE OF S {"))
    assert(m3.contains("ON BATCH UPDATE OF T {"))
  }

  test("malformed variable order input is rejected") {
    val parser = new VariableOrderParser()
    val malformed =
      """2 1
        |0 A int -1 {} 0
        |1 B int 0 {0} 0
        |R 99 A,B
        |""".stripMargin

    val err = intercept[RuntimeException] {
      parser.apply(malformed)
    }

    assert(err.getMessage != null)
    assert(err.getMessage.toLowerCase.contains("no root") || err.getMessage.toLowerCase.contains("none.get"))
  }

  test("variable order input referencing an undeclared key fails with a clear error") {
    val parser = new VariableOrderParser()
    // Variable 0 (A) references key id 99, which is never declared.
    val malformed =
      """1 1
        |0 A int -1 {99} 0
        |R 0 A
        |""".stripMargin

    val err = intercept[RuntimeException] {
      parser.apply(malformed)
    }

    assert(err.getMessage != null)
    // Previously this threw a bare NoSuchElementException ("None.get")
    // instead of a message naming the missing reference.
    assert(err.getMessage.contains("referenced before it was declared"))
  }
}
