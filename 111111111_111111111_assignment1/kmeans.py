import sys

# Constants
MIN_K = 1
MIN_ITER = 1
MAX_ITER = 1000
DEFAULT_ITER = 400

def parse_command_line_args():
    args = sys.argv[1:]

    if len(args) == 0:
        print("An Error Has Occurred")
        return None, None, None

    try:
        k = int(args[0])
        if k <= MIN_K:
            print("Invalid number of clusters!")
            return None, None, None
    except ValueError:
        print("An Error Has Occurred")
        return None, None, None

    if len(args) == 1:
        max_iter = DEFAULT_ITER
        file_arg = None
    elif len(args) == 2:
        max_iter = DEFAULT_ITER
        file_arg = args[1]
    elif len(args) == 3:
        try:
            max_iter = int(args[1])
            if max_iter <= MIN_ITER or max_iter >= MAX_ITER:
                print("Invalid maximum iteration!")
                return None, None, None
        except ValueError:
            print("An Error Has Occurred")
            return None, None, None
        file_arg = args[2]
    else:
        print("An Error Has Occurred")
        return None, None, None

    return k, max_iter, file_arg

def read_vectors(file_arg=None):
    vectors = []

    try:
        if file_arg:
            with open(file_arg, 'r') as f:
                lines = f.readlines()
        else:
            lines = sys.stdin.readlines()

        for line in lines:
            line = line.strip()
            if line:
                try:
                    vector = list(map(float, line.split(',')))
                    vectors.append(vector)
                except ValueError:
                    print("An Error Has Occurred")
                    return None

    except Exception:
        print("An Error Has Occurred")
        return None

    if not vectors:
        print("An Error Has Occurred")
        return None

    return vectors

def validate_vector_dimensions(vectors):
    if not vectors:
        print("An Error Has Occurred")
        return False

    vector_dim = len(vectors[0])
    for vector in vectors:
        if len(vector) != vector_dim:
            print("An Error Has Occurred")
            return False

    return True

def initialize_centroids(vectors, k):
    if k >= len(vectors):  # Must be strictly less than number of vectors
        print("Invalid number of clusters!")
        return None, None

    centroids = [vectors[i][:] for i in range(k)]
    return centroids, k

def euclidean_distance(point, centroid):
    return sum((point[i] - centroid[i]) ** 2 for i in range(len(point))) ** 0.5

def assign_clusters(vectors, centroids):
    k = len(centroids)
    clusters = [[] for _ in range(k)]

    for vector in vectors:
        distances = [euclidean_distance(vector, centroid) for centroid in centroids]
        closest_centroid = distances.index(min(distances))
        clusters[closest_centroid].append(vector)

    return clusters

def update_centroids(clusters, centroids, eps):
    flag = True
    k = len(centroids)
    new_centroids = []

    for j in range(k):
        if clusters[j]:
            dim = len(clusters[j][0])
            new_centroid = [0] * dim
            for point in clusters[j]:
                for i in range(dim):
                    new_centroid[i] += point[i]
            for i in range(dim):
                new_centroid[i] /= len(clusters[j])

            if euclidean_distance(centroids[j], new_centroid) > eps:
                flag = False

            new_centroids.append(new_centroid)
        else:
            new_centroids.append(centroids[j][:])

    return new_centroids, flag

def print_results(clusters, centroids, verbose=True):
    for centroid in centroids:
        formatted_centroid = [f"{x:.4f}" for x in centroid]
        print(','.join(formatted_centroid))

def kmeans_clustering(k, max_iter, vectors, eps=0.001, verbose=True):
    if not validate_vector_dimensions(vectors):
        return None

    centroids, k = initialize_centroids(vectors, k)
    if centroids is None:
        return None

    curr_iter = 0
    converged = False

    while not converged and curr_iter < max_iter:
        curr_iter += 1
        clusters = assign_clusters(vectors, centroids)
        new_centroids, converged = update_centroids(clusters, centroids, eps)
        centroids = new_centroids

    print_results(clusters, centroids, verbose)
    return clusters

def main():
    k, max_iter, file_arg = parse_command_line_args()
    if k is None or max_iter is None:
        return 1

    vectors = read_vectors(file_arg)
    if vectors is None:
        return 1

    clusters = kmeans_clustering(k, max_iter, vectors)
    if clusters is None:
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)