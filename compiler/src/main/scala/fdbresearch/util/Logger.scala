//===----------------------------------------------------------------------===//
//
// Factorized IVM (F-IVM)
//
// https://fdbresearch.github.io/
//
// Copyright (c) 2018-2019, FDB Research Group, University of Oxford
// 
//===----------------------------------------------------------------------===//
package fdbresearch.util

import org.slf4j.LoggerFactory

object Logger {

  // slf4j-simple 2.x moved SimpleLogger from org.slf4j.impl to org.slf4j.simple
  // and switched binding discovery to ServiceLoader (org.slf4j.spi.SLF4JServiceProvider).
  System.setProperty(org.slf4j.simple.SimpleLogger.DEFAULT_LOG_LEVEL_KEY, "INFO")

  val instance = LoggerFactory.getLogger("fdbresearch.fivm")
}
