name := "FIVM"

version := "1.1"

scalaVersion := "2.12.20"

Compile / run / mainClass := Some("fdbresearch.Main")

libraryDependencies ++= Seq(
  "org.scala-lang.modules" %% "scala-parser-combinators" % "2.4.0",
  "com.github.scopt" %% "scopt" % "4.1.0",
  "org.slf4j" % "slf4j-api" % "2.0.17",
  "org.slf4j" % "slf4j-simple" % "2.0.17",
  "org.scalatest" %% "scalatest" % "3.2.19" % Test
)

Test / parallelExecution := false

assembly / assemblyMergeStrategy := {
  // slf4j 2.x discovers its binding via META-INF/services/org.slf4j.spi.SLF4JServiceProvider
  // (ServiceLoader); discarding all of META-INF, as below, drops that file and silently
  // downgrades logging to a no-op provider at runtime.
  case PathList("META-INF", "services", _*) => MergeStrategy.filterDistinctLines
  case PathList("META-INF", _*) => MergeStrategy.discard
  case _ => MergeStrategy.first
}
