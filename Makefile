.PHONY: test-compiler test-runtime smoke verify

test-compiler:
	cd compiler && sbt test

test-runtime:
	cmake -S runtime -B /tmp/fivm-runtime-tests -DFIVM_ENABLE_ZERIALIZE=OFF -DFIVM_BUILD_TESTS=ON
	cmake --build /tmp/fivm-runtime-tests -j4
	ctest --test-dir /tmp/fivm-runtime-tests --output-on-failure

smoke:
	./scripts/smoke-housing.sh

verify: test-compiler test-runtime smoke
