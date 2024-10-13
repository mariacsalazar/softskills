import json

def clean_json(input_file, output_file):
    # 读取 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 清理数据
    for job in data:
        for key, value in job.items():
            if isinstance(value, str):
                # 移除字符串中的换行符和多余的空白
                job[key] = ' '.join(value.split())

    # 保存清理后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"清理完成。结果已保存到 {output_file}")

if __name__ == "__main__":
    input_file = 'job_listings_EN.json'
    output_file = 'job_listings_EN_cleaned.json'
    clean_json(input_file, output_file)
