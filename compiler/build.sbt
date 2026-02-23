name := "FIVM"

version := "1.1"

scalaVersion := "2.12.20"

Compile / run / mainClass := Some("fdbresearch.Main")

libraryDependencies ++= Seq(
  "org.scala-lang.modules" %% "scala-parser-combinators" % "1.1.2",
  "com.github.scopt" %% "scopt" % "3.7.1",
  "org.slf4j" % "slf4j-api" % "1.7.36",
  "org.slf4j" % "slf4j-simple" % "1.7.36"
)

assembly / assemblyMergeStrategy := {
  case PathList("META-INF", _*) => MergeStrategy.discard
  case _ => MergeStrategy.first
}
