package clients

import (
	"context"
	"crypto/md5"
	"encoding/json"
	"fmt"
	"time"

	"github.com/go-redis/redis/v8"
)

type RedisClient struct {
	client *redis.Client
	ctx    context.Context
}

func NewRedisClient(addr string) *RedisClient {
	rdb := redis.NewClient(&redis.Options{
		Addr:     addr,
		Password: "",
		DB:       0,
	})

	return &RedisClient{
		client: rdb,
		ctx:    context.Background(),
	}
}

func (r *RedisClient) Get(key string) ([]byte, error) {
	val, err := r.client.Get(r.ctx, key).Result()
	if err == redis.Nil {
		return nil, nil // Cache miss
	}
	if err != nil {
		return nil, err
	}
	
	return []byte(val), nil
}

func (r *RedisClient) Set(key string, value interface{}, expiration time.Duration) error {
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}
	
	return r.client.Set(r.ctx, key, data, expiration).Err()
}

func (r *RedisClient) MakeKey(prefix string, parts ...string) string {
	combined := prefix
	for _, part := range parts {
		combined += ":" + part
	}
	
	// Hash for consistent key length
	hash := md5.Sum([]byte(combined))
	return fmt.Sprintf("%x", hash)
}

func (r *RedisClient) Close() error {
	return r.client.Close()
}