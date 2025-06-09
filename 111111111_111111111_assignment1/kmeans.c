#include <stdio.h>   
#include <stdlib.h>  
#include <math.h>
/*error occurs 2 and 6 prints twice it needs a change  */
#define MIN_K 1
#define MIN_ITER 1
#define MAX_ITER 1000
#define DEFAULT_ITER 400
#define INITIAL_CAPACITY 10 
#define MAX_LINE_LENGTH 1024 
#define MAX_COORD_LENGTH 100 

int validate_input(int argc, char *argv[], int *k, int *iterations);
double **load_input(int *num_vectors_ptr, int *dimension_ptr);
void kmeans(double **vectors, int num_vectors, int dimension, int k, int iterations);
void free_vectors_array(double **vectors, int num_vectors);
void print_result(double **centroids, int k, int dimension);

/* 
 * Main function: entry point of the program
 * Parses command line arguments, loads input data, 
 * runs k-means clustering, and cleans up resources
 * Returns 0 on success, 1 on failure
 */
int main(int argc, char **argv) {
      int k, iterations;
    int num_vectors = 0;
    int dimension = 0;
    double **vectors;

    if (!validate_input(argc, argv, &k, &iterations)) {
        return 1;
    }

    vectors = load_input(&num_vectors, &dimension);
    if (!vectors) {
        return 1; 
    }

    if (k >= num_vectors) {
        printf("Incorrect number of clusters!\n");
        free_vectors_array(vectors, num_vectors);
        return 1;
    }

    kmeans(vectors, num_vectors, dimension, k, iterations);
    free_vectors_array(vectors, num_vectors);
    return 0;
}

/* 
 * Validates command line arguments
 * argc: argument count
 * argv: argument vector
 * k: output for number of clusters
 * iterations: output for maximum iterations
 * Returns 1 if valid, 0 otherwise
 */
int validate_input(int argc, char *argv[], int *k, int *iterations) {
  char *endptr;
    long k_long;
    long iter_long;

    if (argc < 2 || argc > 3) {
        printf("An Error Has Occurred\n");
        return 0;
    }

    k_long = strtol(argv[1], &endptr, 10);
    if (*endptr != '\0') {
        printf("An Error Has Occurred\n");
        return 0;
    }

    if (k_long <= MIN_K) {
        printf("Incorrect number of clusters!\n");
        return 0;
    }
    *k = (int)k_long;

    if (argc == 3) {
        iter_long = strtol(argv[2], &endptr, 10);
        if (*endptr != '\0') {
            printf("An Error Has Occurred\n");
            return 0;
        }
        if (iter_long <= MIN_ITER || iter_long >= MAX_ITER) {
            printf("Incorrect maximum iteration!\n");
            return 0;
        }
        *iterations = (int)iter_long;
    } else {
        *iterations = DEFAULT_ITER;
    }

    return 1;
}

/* 
 * Counts commas in a string to determine vector dimensions
 * s: input string
 * Returns number of commas found
 */
int count_commas(const char *s) {
    int count = 0;
    int i = 0;

    for (i = 0; s[i] != '\0'; i++) {
        if (s[i] == ',') count++;
    }
    return count;
}

/* 
 * Loads input vectors from stdin
 * num_vectors_ptr: output for number of vectors loaded
 * dimension_ptr: output for vector dimension
 * Returns 2D array of vectors or NULL on failure
 */
double **load_input(int *num_vectors_ptr, int *dimension_ptr) {
    char line[MAX_LINE_LENGTH];
    double **vectors = NULL;
    int vector_count = 0;
    int dim = 0;
    int capacity = INITIAL_CAPACITY;
    int len = 0;
    double val = 0.0;
    int chars_read = 0;
    int i = 0;
    double **new_vectors;
    double *vec;
    const char *p;

    vectors = malloc(capacity * sizeof(double*));
    if (!vectors) {
        printf("An Error Has Occurred\n");
        return NULL;
    }

    while (fgets(line, MAX_LINE_LENGTH, stdin)) {
        len = 0;
        i = 0;

        while (line[len] != '\0') {
            if (line[len] == '\n') {
                line[len] = '\0';
                break;
            }
            len++;
        }

        if (line[0] == '\0') continue; 

        if (vector_count == 0) {
            dim = count_commas(line) + 1;
            if (dim <= 0) {
                printf("An Error Has Occurred\n");
                free(vectors);
                return NULL;
            }
            *dimension_ptr = dim;
        }

        if (vector_count == capacity) {
            capacity *= 2;
            new_vectors = realloc(vectors, capacity * sizeof(double*));
            if (!new_vectors) {
                printf("An Error Has Occurred\n");
                free_vectors_array(vectors, vector_count);
                return NULL;
            }
            vectors = new_vectors;
        }

        vec = malloc(dim * sizeof(double));
        if (!vec) {
            printf("An Error Has Occurred\n");
            free_vectors_array(vectors, vector_count);
            return NULL;
        }

        p = line;
        while (i < dim) {
            chars_read = 0;
            if (sscanf(p, " %lf%n", &val, &chars_read) != 1 || val != val || val == HUGE_VAL || val == -HUGE_VAL) {
                printf("An Error Has Occurred\n");
                free(vec);
                free_vectors_array(vectors, vector_count);
                return NULL;
            }
            vec[i++] = val;

            p += chars_read;
            if (i < dim) {
                if (*p != ',') {
                    printf("An Error Has Occurred\n");
                    free(vec);
                    free_vectors_array(vectors, vector_count);
                    return NULL;
                }
                p += 1;
            }
        }

        while (*p == ' ') p += 1;
        if (*p != '\0') {
            printf("An Error Has Occurred\n");
            free(vec);
            free_vectors_array(vectors, vector_count);
            return NULL;
        }

        vectors[vector_count++] = vec;
    }

    if (vector_count == 0) {
        printf("An Error Has Occurred\n");
        free(vectors);
        return NULL;
    }

    *num_vectors_ptr = vector_count;
    return vectors;
}

/* 
 * Performs k-means clustering algorithm
 * vectors: input data vectors
 * num_vectors: number of vectors
 * dimension: vector dimension
 * k: number of clusters
 * iterations: maximum iterations
 */
void kmeans(double **vectors, int num_vectors, int dimension, int k, int iterations) {
    double **centroids;
    double **new_centroids_sum;
    int *cluster_counts;
    int *assignments;
    int *prev_assignments;
    int i = 0;
    int j = 0;
    int iter = 0;
    int c = 0;
    int d = 0;
    int changes;
    int v = 0;
    int cluster;
    double min_distance_sq; 
    int best_cluster = 0;
    double current_distance_sq = 0.0;
    double diff = 0.0;

    centroids = malloc(k * sizeof(double*));
    new_centroids_sum = malloc(k * sizeof(double*));
    cluster_counts = calloc(k, sizeof(int));
    assignments = calloc(num_vectors, sizeof(int)); 
    prev_assignments = calloc(num_vectors, sizeof(int));

    if (!centroids || !new_centroids_sum || !cluster_counts || !assignments || !prev_assignments) {
        printf("An Error Has Occurred\n");
        if (centroids) {
            for (i = 0; i < k; i++) free(centroids[i]);
            free(centroids);
        }
        if (new_centroids_sum) {
            for (i = 0; i < k; i++) free(new_centroids_sum[i]);
            free(new_centroids_sum);
        }
        free(cluster_counts);
        free(assignments);
        free(prev_assignments);
        return;
    }

    for (i = 0; i < k; i++) {
        centroids[i] = malloc(dimension * sizeof(double));
        new_centroids_sum[i] = malloc(dimension * sizeof(double));
        if (!centroids[i] || !new_centroids_sum[i]) {
            printf("An Error Has Occurred\n");
            for (j = 0; j < i; j++) {
                free(centroids[j]);
                free(new_centroids_sum[j]);
            }
            free(centroids);
            free(new_centroids_sum);
            free(cluster_counts);
            free(assignments);
            free(prev_assignments);
            return;
        }
    }

    for (i = 0; i < k; i++) {
        for (j = 0; j < dimension; j++) {
            centroids[i][j] = vectors[i][j];
        }
    }

    for (iter = 0; iter < iterations; iter++) {
        changes = 0; 

        for (c = 0; c < k; c++) {
            for (d = 0; d < dimension; d++) {
                new_centroids_sum[c][d] = 0.0;
            }
            cluster_counts[c] = 0;
        }

        for (v = 0; v < num_vectors; v++) {
            prev_assignments[v] = assignments[v];
        }

        for (v = 0; v < num_vectors; v++) {
            best_cluster = 0;
            min_distance_sq = 1e308; 
            for (c = 0; c < k; c++) {
                current_distance_sq = 0.0;
                for (d = 0; d < dimension; d++) {
                    diff = vectors[v][d] - centroids[c][d];
                    current_distance_sq += diff * diff;
                }

                if (current_distance_sq < min_distance_sq) {
                    min_distance_sq = current_distance_sq;
                    best_cluster = c;
                }
            }
            assignments[v] = best_cluster;

            if (assignments[v] != prev_assignments[v]) {
                changes+=1;
            }
        }

        for (v = 0; v < num_vectors; v++) {
            cluster = assignments[v];
            for (d = 0; d < dimension; d++) {
                new_centroids_sum[cluster][d] += vectors[v][d];
            }
            cluster_counts[cluster]++;
        }

        for (c = 0; c < k; c++) {
            if (cluster_counts[c] > 0) {
                for (d = 0; d < dimension; d++) {
                    centroids[c][d] = new_centroids_sum[c][d] / cluster_counts[c];
                }
            } else {
                printf("An Error Has Occurred\n");
            }
        }

        if (changes == 0 && iter > 0) { 
            break;
        }
    }

    print_result(centroids, k, dimension);
    for (i = 0; i < k; i++) {
        free(centroids[i]);
        free(new_centroids_sum[i]);
    }
    free(centroids);
    free(new_centroids_sum);
    free(cluster_counts);
    free(assignments);
    free(prev_assignments);
}

/* 
 * Frees memory allocated for vectors
 * vectors: array of vectors to free
 * num_vectors: number of vectors in array
 */
void free_vectors_array(double **vectors, int num_vectors) {
    int i = 0;
    if (vectors) {
        for (i = 0; i < num_vectors; i++) {
            free(vectors[i]);
        }
        free(vectors);
    }
}

/* 
 * Prints clustering results
 * centroids: final cluster centroids
 * k: number of clusters
 * dimension: vector dimension
 */
void print_result(double **centroids, int k, int dimension) {
    int i = 0;
    int j = 0;

    for (i = 0; i < k; i++) {
        for (j = 0; j < dimension; j++) {
            printf("%.4f", centroids[i][j]);
            if (j < dimension - 1) printf(",");
        }
        printf("\n");
    }
}