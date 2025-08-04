#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易猫商品监控 - Vercel部署版本
云端监控系统，全球访问
"""

import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from flask import Flask, render_template_string, jsonify, request
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 全局变量存储数据
products_data = []
last_update = None

class VercelScraper:
    def __init__(self):
        self.base_url = "https://www.jiaoyimao.com/jg2000595-5/"
        self.ua = UserAgent()
    
    def extract_publish_time_from_url(self, product_url):
        """从商品URL提取发布时间"""
        try:
            product_id = product_url.split('/')[-1].replace('.html', '')
            timestamp_str = product_id[:10]
            timestamp = int(timestamp_str)
            publish_time = datetime.fromtimestamp(timestamp)
            return publish_time.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "解析失败"
    
    def calculate_discount(self, price, wuwei_points):
        """计算几折：价格 ÷ (无畏点数 ÷ 10)"""
        try:
            if wuwei_points == 0:
                return 0.0
            discount = price / (wuwei_points / 10)
            return discount
        except:
            return 0.0
    
    def is_target_product(self, price, discount):
        """判断是否为目标商品：大于四折 且 价格<1000元"""
        try:
            return discount > 4.0 and price < 1000
        except:
            return False
    
    def extract_product_detail(self, product_url):
        """提取商品详情"""
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': self.base_url,
            })
            
            response = session.get(product_url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            # 提取价格
            price = 0.0
            price_patterns = [
                r'价格[：:]\s*(\d+(?:\.\d+)?)元',
                r'(\d+(?:\.\d+)?)元',
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, page_text)
                if match:
                    price = float(match.group(1))
                    break
            
            # 提取已用无畏点
            wuwei_points = 0
            wuwei_patterns = [
                r'已用无畏点[：:]\s*(\d+(?:,\d+)*)',
                r'无畏点[：:]\s*(\d+(?:,\d+)*)',
            ]
            
            for pattern in wuwei_patterns:
                match = re.search(pattern, page_text)
                if match:
                    points_str = match.group(1).replace(',', '')
                    wuwei_points = int(points_str)
                    break
            
            # 提取发布时间
            publish_time = self.extract_publish_time_from_url(product_url)
            
            # 计算几折
            discount = self.calculate_discount(price, wuwei_points)
            
            # 判断是否为目标商品
            is_target = self.is_target_product(price, discount)
            
            return {
                '商品链接': product_url,
                '价格': price,
                '无畏点': wuwei_points,
                '发布时间': publish_time,
                '几折': discount,
                '是否目标': is_target,
                '爬取时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return None
    
    def get_sample_products(self):
        """获取示例商品数据（用于演示）"""
        sample_urls = [
            "https://www.jiaoyimao.com/jg2000595-5/1754308923230271.html",
            "https://www.jiaoyimao.com/jg2000595-5/1754303127616003.html",
            "https://www.jiaoyimao.com/jg2000595-5/1754310977123456.html",
        ]
        
        products = []
        for url in sample_urls:
            try:
                product = self.extract_product_detail(url)
                if product:
                    products.append(product)
                time.sleep(1)  # 避免请求过快
            except:
                continue
        
        return products

# 创建爬虫实例
scraper = VercelScraper()

@app.route('/')
def index():
    """主页面"""
    return render_template_string(get_html_template())

@app.route('/api/products')
def api_products():
    """API接口 - 获取商品数据"""
    global products_data, last_update
    
    try:
        # 如果数据为空或超过10分钟，重新获取
        if not products_data or not last_update or (datetime.now() - last_update).seconds > 600:
            products_data = scraper.get_sample_products()
            last_update = datetime.now()
        
        total_count = len(products_data)
        target_count = sum(1 for p in products_data if p['是否目标'])
        
        return jsonify({
            'success': True,
            'data': {
                'products': products_data,
                'total_count': total_count,
                'target_count': target_count,
                'target_percentage': (target_count/total_count*100) if total_count > 0 else 0,
                'last_update': last_update.strftime("%Y-%m-%d %H:%M:%S") if last_update else "未更新"
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/refresh')
def api_refresh():
    """API接口 - 手动刷新数据"""
    global products_data, last_update
    
    try:
        products_data = scraper.get_sample_products()
        last_update = datetime.now()
        
        total_count = len(products_data)
        target_count = sum(1 for p in products_data if p['是否目标'])
        
        return jsonify({
            'success': True,
            'message': '数据刷新成功',
            'data': {
                'total_count': total_count,
                'target_count': target_count,
                'last_update': last_update.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def get_html_template():
    """获取HTML模板"""
    return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交易猫商品监控 - 云端版</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: #f8f9fa;
            flex-wrap: wrap;
        }
        .stat-item {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            min-width: 120px;
            margin: 10px;
            border-left: 4px solid #667eea;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        .controls {
            padding: 20px;
            text-align: center;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            margin: 5px;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .btn.success {
            background: #28a745;
        }
        .btn.warning {
            background: #ffc107;
            color: #212529;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        th {
            background: #667eea;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
        }
        .target-row {
            background: linear-gradient(90deg, #fff3cd 0%, #ffffff 100%);
            border-left: 4px solid #ffc107;
        }
        .target-mark {
            color: #dc3545;
            font-weight: bold;
            font-size: 16px;
        }
        .price {
            font-weight: bold;
            color: #28a745;
            font-size: 1.1em;
        }
        .discount {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
        }
        .discount-high {
            background: #f8d7da;
            color: #721c24;
        }
        .discount-low {
            background: #d4edda;
            color: #155724;
        }
        .link {
            color: #007bff;
            text-decoration: none;
            word-break: break-all;
            max-width: 300px;
            display: inline-block;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .link:hover {
            text-decoration: underline;
        }
        .status {
            text-align: center;
            padding: 15px;
            margin: 20px;
            border-radius: 8px;
            font-weight: bold;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 1.2em;
            color: #666;
        }
        .footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            border-top: 1px solid #dee2e6;
        }
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 10px;
            }
            .header h1 {
                font-size: 2em;
            }
            .stats {
                flex-direction: column;
            }
            table {
                font-size: 12px;
            }
            th, td {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 交易猫商品监控系统</h1>
            <p>☁️ 云端版 - 全球访问 | 监控条件: 大于四折且价格小于1000元</p>
        </div>
        
        <div class="stats" id="statsContainer">
            <div class="stat-item">
                <div class="stat-number" id="totalCount">-</div>
                <div class="stat-label">总商品数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="targetCount">-</div>
                <div class="stat-label">🎯 目标商品</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="targetPercentage">-</div>
                <div class="stat-label">目标比例</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshData()">🔄 刷新数据</button>
            <button class="btn" onclick="showOnlyTargets()">🎯 只看目标商品</button>
            <button class="btn" onclick="showAllProducts()">📦 显示全部</button>
            <span id="lastUpdate" style="margin-left: 20px; color: #666;"></span>
        </div>
        
        <div id="statusMessage" class="status info">
            正在加载数据...
        </div>
        
        <div id="tableContainer">
            <div class="loading">📦 加载中...</div>
        </div>
        
        <div class="footer">
            <p>🌐 部署在 Vercel 云平台 | 💻 交易猫商品监控系统</p>
            <p>最后更新: <span id="footerUpdate">-</span></p>
        </div>
    </div>
    
    <script>
        let allProducts = [];
        let showOnlyTargetsFlag = false;
        
        function refreshData() {
            updateStatus('info', '🔄 正在刷新数据...');
            
            fetch('/api/refresh')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadProducts();
                        updateStatus('success', `✅ ${data.message} - ${data.data.last_update}`);
                    } else {
                        updateStatus('error', `❌ 刷新失败: ${data.error}`);
                    }
                })
                .catch(error => {
                    updateStatus('error', `❌ 网络错误: ${error.message}`);
                });
        }
        
        function loadProducts() {
            fetch('/api/products')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        allProducts = data.data.products;
                        updateStats(data.data);
                        updateTable(showOnlyTargetsFlag ? allProducts.filter(p => p['是否目标']) : allProducts);
                        updateStatus('success', `✅ 数据加载成功 - ${data.data.last_update}`);
                    } else {
                        updateStatus('error', `❌ 数据加载失败: ${data.error}`);
                    }
                })
                .catch(error => {
                    updateStatus('error', `❌ 网络错误: ${error.message}`);
                });
        }
        
        function updateStats(data) {
            document.getElementById('totalCount').textContent = data.total_count;
            document.getElementById('targetCount').textContent = data.target_count;
            document.getElementById('targetPercentage').textContent = data.target_percentage.toFixed(1) + '%';
            document.getElementById('lastUpdate').textContent = `最后更新: ${data.last_update}`;
            document.getElementById('footerUpdate').textContent = data.last_update;
        }
        
        function updateTable(products) {
            const container = document.getElementById('tableContainer');
            
            if (products.length === 0) {
                container.innerHTML = '<div class="loading">暂无商品数据</div>';
                return;
            }
            
            let tableHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>目标</th>
                            <th>价格</th>
                            <th>无畏点</th>
                            <th>几折</th>
                            <th>发布时间</th>
                            <th>商品链接</th>
                            <th>爬取时间</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            products.forEach(product => {
                const isTarget = product['是否目标'];
                const rowClass = isTarget ? 'target-row' : '';
                const targetMark = isTarget ? '🎯目标' : '';
                const discountClass = product['几折'] > 4.0 ? 'discount-high' : 'discount-low';
                
                tableHTML += `
                    <tr class="${rowClass}">
                        <td class="target-mark">${targetMark}</td>
                        <td class="price">${product['价格']}元</td>
                        <td>${product['无畏点'].toLocaleString()}</td>
                        <td class="discount ${discountClass}">${product['几折'].toFixed(2)}折</td>
                        <td>${product['发布时间']}</td>
                        <td><a href="${product['商品链接']}" target="_blank" class="link" title="${product['商品链接']}">${product['商品链接']}</a></td>
                        <td>${product['爬取时间']}</td>
                    </tr>
                `;
            });
            
            tableHTML += '</tbody></table>';
            container.innerHTML = tableHTML;
        }
        
        function updateStatus(type, message) {
            const statusEl = document.getElementById('statusMessage');
            statusEl.className = `status ${type}`;
            statusEl.textContent = message;
        }
        
        function showOnlyTargets() {
            showOnlyTargetsFlag = true;
            updateTable(allProducts.filter(p => p['是否目标']));
            updateStatus('info', '🎯 只显示目标商品');
        }
        
        function showAllProducts() {
            showOnlyTargetsFlag = false;
            updateTable(allProducts);
            updateStatus('info', '📦 显示全部商品');
        }
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadProducts();
            
            // 每5分钟自动刷新一次
            setInterval(loadProducts, 300000);
        });
    </script>
</body>
</html>
    '''

# Vercel需要的handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == "__main__":
    app.run(debug=True)
