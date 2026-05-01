#!/usr/bin/env python3
"""
批量抓取about.me用户页面
GitHub Actions版本
"""
import urllib.request
import urllib.error
import json
import time
import csv
import os
from datetime import datetime

def fetch_aboutme(username):
    """抓取单个about.me用户"""
    url = f"https://about.me/{username}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Bot/1.0)',
        'Accept': 'text/html,application/xhtml+xml',
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            
            # 提取页面标题
            title = ""
            if '<title>' in content:
                start = content.find('<title>') + 7
                end = content.find('</title>', start)
                title = content[start:end].strip()
            
            # 检查是否真实用户（不是登录页/注册页）
            if 'Log In' in title or 'Sign Up' in title or 'Get started' in title:
                return None
            
            # 提取描述
            description = ""
            if 'name="description"' in content:
                start = content.find('content="', content.find('name="description"')) + 8
                end = content.find('"', start)
                description = content[start:end][:200]
            
            return {
                'username': username,
                'url': url,
                'title': title,
                'description': description,
                'status': 'found'
            }
    except urllib.error.HTTPError:
        return None
    except Exception as e:
        print(f"  Error fetching {username}: {e}")
        return None

def generate_username_list():
    """生成用户名列表"""
    names = []
    
    # 常见英文名
    first_names = [
        'gary', 'matt', 'jennifer', 'kevin', 'steve', 'alex', 'jason', 'jamie', 
        'taylor', 'jordan', 'morgan', 'alexis', 'blake', 'parker', 'seth', 'guy',
        'neil', 'adam', 'ben', 'tom', 'nick', 'paul', 'dustin', 'jack', 'zeldman',
        'veerle', 'ann', 'reed', 'marissa', 'drew', 'chad', 'phil', 'lisa', 'sarah',
        'emily', 'sophia', 'olivia', 'emma', 'andrew', 'rachel', 'julia', 'natalie',
        'victoria', 'grace', 'chloe', 'jacob', 'ethan', 'noah', 'sam', 'frank',
        'dean', 'ross', 'kurt', 'chad', 'drew', 'sundar', 'satya', 'malcolm',
        'jimmy', 'phil', 'giles', 'richard', 'henry', 'lucas', 'anna', 'zoe',
        'casey', 'mike', 'john', 'brian', 'daniel', 'william', 'robert', 'james',
        'jeff', 'elon', 'tim', 'mark', 'larry', 'sergey', 'ycombinator', 'arianna'
    ]
    
    # 常见职业词
    jobs = ['writer', 'designer', 'developer', 'photographer', 'artist', 'consultant',
            'entrepreneur', 'marketer', 'developer', 'engineer', 'manager', 'director',
            'producer', 'coach', 'teacher', 'analyst', 'specialist', 'coordinator']
    
    # 常见组合
    for name in first_names:
        names.append(name)
        for job in jobs[:5]:  # 限制数量
            names.append(f"{name}{job}")
            names.append(f"{name}_{job}")
    
    # 添加数字后缀
    extended = []
    for name in names[:200]:  # 限制总数
        extended.append(name)
        for i in range(1, 5):
            extended.append(f"{name}{i}")
    
    return list(set(extended))[:500]  # 最多500个

def main():
    print(f"[{datetime.now()}] 开始抓取about.me页面...")
    
    # 读取已存在的用户名（如果有）
    existing = set()
    if os.path.exists('aboutme_results.csv'):
        with open('aboutme_results.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row['username'])
        print(f"已跳过 {len(existing)} 个已抓取的用户名")
    
    # 生成用户名列表
    usernames = generate_username_list()
    print(f"待抓取: {len(usernames)} 个用户名")
    
    results = []
    count = 0
    
    for username in usernames:
        if username in existing:
            continue
            
        print(f"  抓取: {username}...", end=' ')
        result = fetch_aboutme(username)
        
        if result:
            results.append(result)
            print(f"✓")
            print(f"    标题: {result['title'][:50]}")
        else:
            print(f"✗")
        
        count += 1
        time.sleep(0.5)  # 避免请求过快
        
        # 每100个保存一次
        if count % 100 == 0:
            save_results(results)
            print(f"  已保存 {len(results)} 个结果")
    
    # 保存结果
    save_results(results)
    print(f"\n完成！共找到 {len(results)} 个有效页面")
    print(f"结果保存在: aboutme_results.csv")

def save_results(results):
    """保存结果到CSV"""
    with open('aboutme_results.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'url', 'title', 'description', 'status'])
        if f.tell() == 0:  # 新文件
            writer.writeheader()
        for r in results:
            writer.writerow(r)

if __name__ == '__main__':
    main()
