import sys

# Constants definition
MIN_K = 1          # Minimum allowed number of clusters
MIN_ITER = 1       # Minimum allowed iteration count
MAX_ITER = 1000    # Maximum allowed iteration count
DEFAULT_ITER = 400 # Default number of iterations if not specified

def parse_command_line_args():
    """Parse and validate command line arguments.
    Returns:
        tuple: (k, max_iter, file_arg) or (None, None, None) on error
    """
    args = sys.argv[1:]  # Skip script name

    # Handle no arguments case
    if len(args) == 0:
        print("An Error Has Occurred")
        return None, None, None

    try:
        # Parse k (number of clusters)
        k = int(args[0])
        if k <= MIN_K:  # Validate k
            print("Invalid number of clusters!")
            return None, None, None
    except ValueError:  # Handle non-integer k
        print("An Error Has Occurred")
        return None, None, None

    # Argument handling scenarios:
    if len(args) == 1:        # Only k provided
        max_iter = DEFAULT_ITER
        file_arg = None
    elif len(args) == 2:      # k and filename provided
        max_iter = DEFAULT_ITER
        file_arg = args[1]
    elif len(args) == 3:      # k, max_iter, and filename provided
        try:
            max_iter = int(args[1])
            # Validate iteration count
            if max_iter <= MIN_ITER or max_iter >= MAX_ITER:
                print("Invalid maximum iteration!")
                return None, None, None
        except ValueError:    # Handle non-integer max_iter
            print("An Error Has Occurred")
            return None, None, None
        file_arg = args[2]
    else:  # Too many arguments
        print("An Error Has Occurred")
        return None, None, None

    return k, max_iter, file_arg

def read_vectors(file_arg=None):
    """Read vectors from file or standard input.
    Args:
        file_arg: filename or None for stdin
    Returns:
        list: list of vectors or None on error
    """
    vectors = []

    try:
        if file_arg:
            # Read from specified file
            with open(file_arg, 'r') as f:
                lines = f.readlines()
        else:
            # Read from standard input
            lines = sys.stdin.readlines()

        # Process each line
        for line in lines:
            line = line.strip()
            if line:
                try:
                    # Convert comma-separated values to float vector
                    vector = list(map(float, line.split(',')))
                    vectors.append(vector)
                except ValueError:  # Handle conversion error
                    print("An Error Has Occurred")
                    return None

    except Exception:  # Catch all file/IO errors
        print("An Error Has Occurred")
        return None

    # Check for empty input
    if not vectors:
        print("An Error Has Occurred")
        return None

    return vectors

def validate_vector_dimensions(vectors):
    """Verify all vectors have same dimensionality.
    Args:
        vectors: list of vectors
    Returns:
        bool: True if valid, False otherwise
    """
    if not vectors:
        print("An Error Has Occurred")
        return False

    # Get dimension of first vector
    vector_dim = len(vectors[0])
    for vector in vectors:
        # Compare all vector lengths to first
        if len(vector) != vector_dim:
            print("An Error Has Occurred")
            return False

    return True

def initialize_centroids(vectors, k):
    """Initialize centroids using first k vectors.
    Args:
        vectors: list of input vectors
        k: number of clusters
    Returns:
        tuple: (centroids, k) or (None, None) on error
    """
    # Validate k doesn't exceed number of vectors
    if k >= len(vectors):
        print("Invalid number of clusters!")
        return None, None

    # Select first k vectors as initial centroids
    centroids = [vectors[i][:] for i in range(k)]
    return centroids, k

def euclidean_distance(point, centroid):
    """Calculate Euclidean distance between point and centroid.
    Args:
        point: data point vector
        centroid: cluster center vector
    Returns:
        float: distance value
    """
    return sum((point[i] - centroid[i]) ** 2 for i in range(len(point))) ** 0.5

def assign_clusters(vectors, centroids):
    """Assign vectors to nearest centroids.
    Args:
        vectors: list of input vectors
        centroids: current cluster centers
    Returns:
        list: clusters (list of vectors per cluster)
    """
    k = len(centroids)
    # Initialize empty clusters
    clusters = [[] for _ in range(k)]

    for vector in vectors:
        # Calculate distances to all centroids
        distances = [euclidean_distance(vector, centroid) for centroid in centroids]
        # Find closest centroid index
        closest_centroid = distances.index(min(distances))
        # Add vector to corresponding cluster
        clusters[closest_centroid].append(vector)

    return clusters

def update_centroids(clusters, centroids, eps):
    """Calculate new centroids and check convergence.
    Args:
        clusters: current cluster assignments
        centroids: current cluster centers
        eps: convergence threshold
    Returns:
        tuple: (new_centroids, convergence_flag)
    """
    flag = True  # Convergence flag (assume converged)
    k = len(centroids)
    new_centroids = []

    for j in range(k):
        if clusters[j]:  # Cluster has vectors
            dim = len(clusters[j][0])
            # Initialize new centroid vector
            new_centroid = [0] * dim
            # Sum all vectors in cluster
            for point in clusters[j]:
                for i in range(dim):
                    new_centroid[i] += point[i]
            # Calculate mean (centroid position)
            for i in range(dim):
                new_centroid[i] /= len(clusters[j])

            # Check if centroid moved significantly
            if euclidean_distance(centroids[j], new_centroid) > eps:
                flag = False  # Not converged

            new_centroids.append(new_centroid)
        else:  # Empty cluster - keep old centroid
            new_centroids.append(centroids[j][:])

    return new_centroids, flag

def print_results(clusters, centroids, verbose=True):
    """Print final centroids with 4 decimal precision.
    Args:
        clusters: final cluster assignments
        centroids: final cluster centers
        verbose: unused in this implementation
    """
    for centroid in centroids:
        # Format each coordinate to 4 decimal places
        formatted_centroid = [f"{x:.4f}" for x in centroid]
        # Join coordinates with commas
        print(','.join(formatted_centroid))

def kmeans_clustering(k, max_iter, vectors, eps=0.001, verbose=True):
    """Main k-means clustering algorithm.
    Args:
        k: number of clusters
        max_iter: maximum iterations
        vectors: input data
        eps: convergence threshold
        verbose: unused
    Returns:
        clusters or None on error
    """
    # Validate vector dimensions
    if not validate_vector_dimensions(vectors):
        return None

    # Initialize centroids
    centroids, k = initialize_centroids(vectors, k)
    if centroids is None:
        return None

    curr_iter = 0
    converged = False

    # Main k-means loop
    while not converged and curr_iter < max_iter:
        curr_iter += 1
        # Assign vectors to clusters
        clusters = assign_clusters(vectors, centroids)
        # Update centroids and check convergence
        new_centroids, converged = update_centroids(clusters, centroids, eps)
        centroids = new_centroids

    # Output final centroids
    print_results(clusters, centroids, verbose)
    return clusters

def main():
    """Program entry point."""
    # Parse command line arguments
    k, max_iter, file_arg = parse_command_line_args()
    if k is None or max_iter is None:
        return 1  # Error exit code

    # Read input vectors
    vectors = read_vectors(file_arg)
    if vectors is None:
        return 1

    # Run k-means algorithm
    clusters = kmeans_clustering(k, max_iter, vectors)
    if clusters is None:
        return 1

    return 0  # Success exit code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)