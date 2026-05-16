import ray
import pandas as pd
from collections import defaultdict
import sys
import time

@ray.remote
def process_chunk(chunk_df):

    stats = defaultdict(lambda: {
        'total': 0,
        'slow': 0,
        'server_error': 0,
        'timeout': 0
    })
    
    for _, row in chunk_df.iterrows():
        service = row['service_name']
        stats[service]['total'] += 1
        
        # response_time_ms > 800
        if row['response_time_ms'] > 800:
            stats[service]['slow'] += 1
        
        # status_code == 500
        if row['status_code'] == 500:
            stats[service]['server_error'] += 1
        
        # error_type : 'Timeout'
        if row['error_type'] == 'Timeout':
            stats[service]['timeout'] += 1
    
    return dict(stats)


def aggregate_results(all_chunk_stats):
    final_stats = defaultdict(lambda: {
        'total': 0,
        'slow': 0,
        'server_error': 0,
        'timeout': 0
    })
    
    for chunk_stats in all_chunk_stats:
        for service, stats in chunk_stats.items():
            final_stats[service]['total'] += stats['total']
            final_stats[service]['slow'] += stats['slow']
            final_stats[service]['server_error'] += stats['server_error']
            final_stats[service]['timeout'] += stats['timeout']
    
    return final_stats


def detect_degraded_services(final_stats):
    degraded = []
    
    for service, stats in final_stats.items():
        total = stats['total']
        if total == 0:
            continue
            
        slow_rate = stats['slow'] / total
        error_rate = stats['server_error'] / total
        timeout_count = stats['timeout']

        if slow_rate > 0.2:
            degraded.append(f"{service}, high slow request rate")
        elif error_rate > 0.1:
            degraded.append(f"{service}, high server error rate")
        elif timeout_count >= 5:
            degraded.append(f"{service}, repeated timeout errors")
    
    return degraded


def main():
    if len(sys.argv) < 2:
        print("Usage: python ray_extension.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    print(f"Processing file: {file_path}")

    ray.init()

    start_time = time.time()

    chunk_size = 1000
    chunks = []
    
    print("Reading CSV file in chunks...")
    for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
        chunks.append(chunk)
        if (i + 1) % 10 == 0:
            print(f"  Loaded {i + 1} chunks...")
    
    print(f"Total chunks: {len(chunks)}")

    print("Processing chunks in parallel with Ray...")
    futures = [process_chunk.remote(chunk) for chunk in chunks]
    chunk_stats = ray.get(futures)

    print("Aggregating results...")
    final_stats = aggregate_results(chunk_stats)

    print("Detecting degraded services...")
    degraded_services = detect_degraded_services(final_stats)

    end_time = time.time()

    print("\n" + "="*50)
    print("DEGRADED SERVICES DETECTION RESULTS")
    print("="*50)
    for service in degraded_services:
        print(service)
    
    if not degraded_services:
        print("No degraded services detected.")
    
    print("\n" + "="*50)
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
    print("="*50)
    

    print("\nDetailed statistics (for validation):")
    for service, stats in final_stats.items():
        total = stats['total']
        if total > 0:
            slow_rate = stats['slow'] / total
            error_rate = stats['server_error'] / total
            print(f"  {service}: total={total}, slow_rate={slow_rate:.1%}, "
                  f"error_rate={error_rate:.1%}, timeout={stats['timeout']}")
    
    ray.shutdown()


if __name__ == "__main__":
    main()