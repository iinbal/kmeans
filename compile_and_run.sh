#!/bin/bash

set -eu

RED="\033[31m"
GREEN="\033[32m"
RESET="\033[0m"

PROJECT_DIRECTORY=111111111_111111111_assignment1

SCRIPT_DIR=`dirname $0`

function testKmeans() {
	k_and_maxIter=$1
	inputFileName=$2
	expectedName=$3

	echo "Running test: arguments=\"${k_and_maxIter}\" inputFileName=${inputFileName} expectedName=${expectedName}"
	valgrind --quiet --leak-check=full ./out/kmeans $k_and_maxIter < tests/input_${inputFileName}.txt | diff tests/output_${expectedName}.txt - && echo -e "${GREEN}Test Passed.${RESET}" || echo -e "${RED}C TEST FAILED!!!${RESET}"
	python3 out/kmeans.py $k_and_maxIter tests/input_${inputFileName}.txt | diff tests/output_${expectedName}.txt - && echo -e "${GREEN}Test Passed.${RESET}" || echo -e "${RED}python TEST FAILED!!!${RESET}"
	echo
}

pushd ${SCRIPT_DIR}
gcc -ansi -Wall -Wextra -Werror -pedantic-errors ${PROJECT_DIRECTORY}/kmeans.c -lm -o out/kmeans
gcc -ansi -g -Wall -Wextra -Werror -pedantic-errors ${PROJECT_DIRECTORY}/kmeans.c -lm -o out/kmeans_debug
cp  ${PROJECT_DIRECTORY}/kmeans.py out/kmeans.py

testKmeans "3 600" 1 1
testKmeans "7" 2 2
testKmeans "15 300" 3 3
testKmeans "2 2" 4 4__2_2
testKmeans "7 999" 4 4__7_999

testKmeans "8 2" 4 invalid_clusters
testKmeans "1 2" 4 invalid_clusters
testKmeans "-2 2" 4 invalid_clusters

testKmeans "2 1000" 4 invalid_maxIter
testKmeans "2 1" 4 invalid_maxIter
testKmeans "2 -2" 4 invalid_maxIter

testKmeans "2 2" 5_invalid general_error
testKmeans "" 5_invalid general_error
testKmeans "a 2" 5_invalid general_error
testKmeans "2 a" 5_invalid general_error
testKmeans "2 2 3" 5_invalid general_error
popd