#include <stdio.h>   
#include <stdlib.h>  
#include <math.h>

#define MIN_K 1
#define MIN_ITER 2
#define MAX_ITER 1000
#define DEFAULT_ITER 400
#define INITIAL_CAPACITY 10
#define MAX_LINE_LENGTH 1024

int validate_input(int argc, char *argv[], int *k, int *iterations);
int count_commas(const char *s);
double **load_input(const char *filename, int *num_vectors_out, int *dimension_out);
void kmeans(double **vectors, int num_vectors, int dimension, int k, int iterations);
void free_vectors_array(double **vectors, int num_vectors);
void print_result(double **centroids, int k, int dimension);
