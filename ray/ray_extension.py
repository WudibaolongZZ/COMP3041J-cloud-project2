import ray
import pandas as pd
from collections import defaultdict
import sys
import time

@ray.remote
def process_chunk(chunk_df):
    """
    处理一个数据块，返回该块中各服务的统计信息
    """
    stats = defaultdict(lambda: {
        'total': 0,
        'slow': 0,
        'server_error': 0,
        'timeout': 0
    })
    
    for _, row in chunk_df.iterrows():
        service = row['service_name']
        stats[service]['total'] += 1
        
        # 慢请求: response_time_ms > 800
        if row['response_time_ms'] > 800:
            stats[service]['slow'] += 1
        
        # 服务器错误: status_code == 500
        if row['status_code'] == 500:
            stats[service]['server_error'] += 1
        
        # Timeout错误: error_type 字段为 'Timeout'
        if row['error_type'] == 'Timeout':
            stats[service]['timeout'] += 1
    
    return dict(stats)


def aggregate_results(all_chunk_stats):
    """
    聚合所有分块的结果
    """
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
    """
    判断哪些服务降级
    条件：
    1. 慢请求率 > 20%
    2. 服务器错误率 > 10%
    3. 至少有5个Timeout错误
    """
    degraded = []
    
    for service, stats in final_stats.items():
        total = stats['total']
        if total == 0:
            continue
            
        slow_rate = stats['slow'] / total
        error_rate = stats['server_error'] / total
        timeout_count = stats['timeout']
        
        # 收集所有满足的条件
        if slow_rate > 0.2:
            degraded.append(f"{service}, high slow request rate")
        elif error_rate > 0.1:
            degraded.append(f"{service}, high server error rate")
        elif timeout_count >= 5:
            degraded.append(f"{service}, repeated timeout errors")
    
    return degraded


def main():
    # 获取文件路径
    if len(sys.argv) < 2:
        print("Usage: python ray_extension.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    print(f"Processing file: {file_path}")
    
    # 初始化Ray
    # 本地调试时可以用 local_mode=True 串行执行方便调试
    # 正式运行时用 ray.init()
    ray.init()
    
    # 记录开始时间
    start_time = time.time()
    
    # 分块读取数据（避免内存溢出）
    chunk_size = 1000  # 每块1000行，可根据内存调整
    chunks = []
    
    print("Reading CSV file in chunks...")
    for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
        chunks.append(chunk)
        if (i + 1) % 10 == 0:
            print(f"  Loaded {i + 1} chunks...")
    
    print(f"Total chunks: {len(chunks)}")
    
    # 并行处理所有块
    print("Processing chunks in parallel with Ray...")
    futures = [process_chunk.remote(chunk) for chunk in chunks]
    chunk_stats = ray.get(futures)
    
    # 聚合结果
    print("Aggregating results...")
    final_stats = aggregate_results(chunk_stats)
    
    # 检测降级服务
    print("Detecting degraded services...")
    degraded_services = detect_degraded_services(final_stats)
    
    # 记录结束时间
    end_time = time.time()
    
    # 输出结果
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
    
    # 可选：打印详细统计（用于调试）
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