package vector

import (
	"math"
)

// calculate cosine similarity between two vectors
func CosineSimilarity(a, b []float64) float64 {
	if len(a) != len(b) {
		return 0.0
	}

	var dotProduct, normA, normB float64

	for i := 0; i < len(a); i++ {
		dotProduct += a[i] * b[i]
		normA += a[i] * a[i]
		normB += b[i] * b[i]
	}

	if normA == 0 || normB == 0 {
		return 0.0
	}

	return dotProduct / (math.Sqrt(normA) * math.Sqrt(normB))
}

// calculate Euclidean distance between two vectors
func EuclideanDistance(a, b []float64) float64 {
	if len(a) != len(b) {
		return math.MaxFloat64
	}

	var sum float64
	for i := 0; i < len(a); i++ {
		diff := a[i] - b[i]
		sum += diff * diff
	}

	return math.Sqrt(sum)
}

// normalize a vector to unit length
func Normalize(vector []float64) []float64 {
	var norm float64
	for _, val := range vector {
		norm += val * val
	}
	norm = math.Sqrt(norm)

	if norm == 0 {
		return vector
	}

	normalized := make([]float64, len(vector))
	for i, val := range vector {
		normalized[i] = val / norm
	}

	return normalized
}
