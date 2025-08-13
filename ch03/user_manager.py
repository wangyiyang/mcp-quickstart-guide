#!/usr/bin/env python3
"""
第三课配套代码：用户管理系统MCP服务器
==================================

完整的用户管理系统，演示数据库操作、API集成、文件处理等企业级功能。

作者: MCP开发入门系列
版本: 1.0
"""

import sqlite3
import json
import csv
import os
import time
import re
from datetime import datetime
from fastmcp import FastMCP
from typing import List, Dict, Optional

# 创建MCP服务器
mcp = FastMCP("用户管理系统")

# 数据库初始化
def init_database():
    """初始化用户数据库"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON users(status)')
    
    # 插入测试数据
    test_users = [
        ('zhangsan', 'zhang@example.com', '张三'),
        ('lisi', 'li@example.com', '李四'),
        ('wangwu', 'wang@example.com', '王五'),
        ('zhaoliu', 'zhao@example.com', '赵六'),
        ('alice', 'alice@example.com', 'Alice Smith'),
        ('bob', 'bob@example.com', 'Bob Johnson')
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO users (username, email, name) VALUES (?, ?, ?)',
        test_users
    )
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

# 工具函数
def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username: str) -> bool:
    """验证用户名格式"""
    return len(username) >= 3 and username.replace('_', '').isalnum()

# ============================================================================
# 查询工具
# ============================================================================

@mcp.tool
def get_user_by_id(user_id: int) -> Dict:
    """根据ID查询用户信息
    
    Args:
        user_id: 用户ID
        
    Returns:
        用户信息字典
        
    Raises:
        ValueError: 用户不存在时
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, name, status, created_at, updated_at 
        FROM users WHERE id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'name': result[3],
            'status': result[4],
            'created_at': result[5],
            'updated_at': result[6]
        }
    else:
        raise ValueError(f"未找到ID为{user_id}的用户")

@mcp.tool
def search_users(keyword: str, limit: int = 10) -> List[Dict]:
    """搜索用户（支持用户名、邮箱、姓名模糊匹配）
    
    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制
        
    Returns:
        匹配的用户列表
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    search_pattern = f'%{keyword}%'
    cursor.execute('''
        SELECT id, username, email, name, status, created_at, updated_at 
        FROM users 
        WHERE username LIKE ? OR email LIKE ? OR name LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (search_pattern, search_pattern, search_pattern, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    users = []
    for row in results:
        users.append({
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'name': row[3],
            'status': row[4],
            'created_at': row[5],
            'updated_at': row[6]
        })
    
    return users

@mcp.tool
def list_users(limit: int = 10, offset: int = 0, status: str = 'all') -> Dict:
    """获取用户列表（支持分页）
    
    Args:
        limit: 每页数量
        offset: 偏移量
        status: 状态筛选（all/active/inactive/suspended）
        
    Returns:
        包含用户列表和分页信息的字典
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # 构建查询条件
    base_query = 'SELECT id, username, email, name, status, created_at, updated_at FROM users'
    count_query = 'SELECT COUNT(*) FROM users'
    
    params = []
    if status != 'all':
        base_query += ' WHERE status = ?'
        count_query += ' WHERE status = ?'
        params.append(status)
    
    # 获取总数
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # 获取分页数据
    base_query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(base_query, params)
    results = cursor.fetchall()
    conn.close()
    
    users = []
    for row in results:
        users.append({
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'name': row[3],
            'status': row[4],
            'created_at': row[5],
            'updated_at': row[6]
        })
    
    return {
        'users': users,
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total,
            'current_page': offset // limit + 1,
            'total_pages': (total + limit - 1) // limit
        }
    }

# ============================================================================
# 管理工具
# ============================================================================

@mcp.tool
def create_user(username: str, email: str, name: str) -> Dict:
    """创建新用户
    
    Args:
        username: 用户名（3-20字符，字母数字下划线）
        email: 邮箱地址
        name: 真实姓名
        
    Returns:
        新创建的用户信息
        
    Raises:
        ValueError: 输入验证失败或用户已存在时
    """
    # 输入验证
    if not validate_username(username):
        raise ValueError("用户名必须是3-20个字符，只能包含字母、数字和下划线")
    
    if not validate_email(email):
        raise ValueError("邮箱格式不正确")
    
    if len(name.strip()) < 2:
        raise ValueError("姓名至少需要2个字符")
    
    name = name.strip()
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, name, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, name, datetime.now().isoformat(), datetime.now().isoformat()))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # 返回新创建的用户信息
        cursor.execute('''
            SELECT id, username, email, name, status, created_at, updated_at 
            FROM users WHERE id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        return {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'name': result[3],
            'status': result[4],
            'created_at': result[5],
            'updated_at': result[6]
        }
        
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            raise ValueError(f"用户名 '{username}' 已存在")
        elif 'email' in str(e):
            raise ValueError(f"邮箱 '{email}' 已被使用")
        else:
            raise ValueError("创建用户失败：数据冲突")
    finally:
        conn.close()

@mcp.tool
def update_user_status(user_id: int, status: str) -> Dict:
    """更新用户状态
    
    Args:
        user_id: 用户ID
        status: 新状态（active/inactive/suspended）
        
    Returns:
        更新后的用户信息
        
    Raises:
        ValueError: 状态无效或用户不存在时
    """
    valid_statuses = ['active', 'inactive', 'suspended']
    if status not in valid_statuses:
        raise ValueError(f"无效状态，必须是：{', '.join(valid_statuses)}")
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET status = ?, updated_at = ? 
        WHERE id = ?
    ''', (status, datetime.now().isoformat(), user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise ValueError(f"未找到ID为{user_id}的用户")
    
    conn.commit()
    
    # 返回更新后的用户信息
    cursor.execute('''
        SELECT id, username, email, name, status, created_at, updated_at 
        FROM users WHERE id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return {
        'id': result[0],
        'username': result[1],
        'email': result[2],
        'name': result[3],
        'status': result[4],
        'created_at': result[5],
        'updated_at': result[6]
    }

@mcp.tool
def update_user_info(user_id: int, name: Optional[str] = None, email: Optional[str] = None) -> Dict:
    """更新用户信息
    
    Args:
        user_id: 用户ID
        name: 新姓名（可选）
        email: 新邮箱（可选）
        
    Returns:
        更新后的用户信息
        
    Raises:
        ValueError: 输入验证失败或用户不存在时
    """
    updates = []
    params = []
    
    if name is not None:
        if len(name.strip()) < 2:
            raise ValueError("姓名至少需要2个字符")
        updates.append("name = ?")
        params.append(name.strip())
    
    if email is not None:
        if not validate_email(email):
            raise ValueError("邮箱格式不正确")
        updates.append("email = ?")
        params.append(email)
    
    if not updates:
        raise ValueError("至少需要提供一个要更新的字段")
    
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(user_id)
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            raise ValueError(f"未找到ID为{user_id}的用户")
        
        conn.commit()
        
        # 返回更新后的用户信息
        cursor.execute('''
            SELECT id, username, email, name, status, created_at, updated_at 
            FROM users WHERE id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        return {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'name': result[3],
            'status': result[4],
            'created_at': result[5],
            'updated_at': result[6]
        }
        
    except sqlite3.IntegrityError:
        raise ValueError(f"邮箱 '{email}' 已被其他用户使用")
    finally:
        conn.close()

# ============================================================================
# 邮件和通知工具
# ============================================================================

@mcp.tool
def send_welcome_email(user_id: int) -> Dict:
    """给新用户发送欢迎邮件
    
    Args:
        user_id: 用户ID
        
    Returns:
        邮件发送结果
        
    Raises:
        ValueError: 用户不存在时
    """
    # 获取用户信息
    user = get_user_by_id(user_id)
    
    # 模拟邮件发送
    email_data = {
        "to": user['email'],
        "subject": f"欢迎加入，{user['name']}！",
        "template": "welcome",
        "variables": {
            "name": user['name'],
            "username": user['username'],
            "login_url": "https://yourapp.com/login"
        }
    }
    
    # 模拟API调用成功
    return {
        "status": "sent",
        "message_id": f"msg_{user_id}_{int(time.time())}",
        "recipient": user['email'],
        "subject": email_data["subject"],
        "sent_at": datetime.now().isoformat()
    }

@mcp.tool
def validate_email_domain(email: str) -> Dict:
    """验证邮箱域名是否有效
    
    Args:
        email: 邮箱地址
        
    Returns:
        验证结果
        
    Raises:
        ValueError: 邮箱格式不正确时
    """
    if not validate_email(email):
        raise ValueError("邮箱格式不正确")
    
    domain = email.split('@')[-1]
    
    # 模拟域名验证
    valid_domains = {
        'gmail.com': 'high',
        'qq.com': 'high', 
        '163.com': 'high',
        'outlook.com': 'high',
        'example.com': 'medium',
        'test.com': 'low'
    }
    
    trust_level = valid_domains.get(domain, 'unknown')
    is_valid = trust_level != 'unknown'
    
    return {
        "email": email,
        "domain": domain,
        "is_valid": is_valid,
        "trust_level": trust_level,
        "recommendations": {
            "high": "推荐域名，可放心使用",
            "medium": "一般域名，建议额外验证",
            "low": "不推荐域名，可能是临时邮箱",
            "unknown": "未知域名，需要人工审核"
        }.get(trust_level, ""),
        "checked_at": datetime.now().isoformat()
    }

# ============================================================================
# 文件操作工具
# ============================================================================

@mcp.tool
def export_users_csv(status: str = 'all', include_emails: bool = True) -> Dict:
    """导出用户数据到CSV文件
    
    Args:
        status: 用户状态筛选（all/active/inactive/suspended）
        include_emails: 是否包含邮箱信息
        
    Returns:
        导出结果信息
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"users_export_{status}_{timestamp}.csv"
    
    # 获取用户数据
    user_data = list_users(limit=10000, status=status)
    users = user_data['users']
    
    # 准备CSV字段
    fieldnames = ['id', 'username', 'name', 'status', 'created_at', 'updated_at']
    if include_emails:
        fieldnames.insert(2, 'email')
    
    # 写入CSV文件
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for user in users:
            row = {field: user[field] for field in fieldnames if field in user}
            writer.writerow(row)
    
    file_size = os.path.getsize(filename)
    
    return {
        "filename": filename,
        "record_count": len(users),
        "file_size_bytes": file_size,
        "file_size_human": f"{file_size / 1024:.1f} KB",
        "fields": fieldnames,
        "filters": {"status": status, "include_emails": include_emails},
        "exported_at": datetime.now().isoformat()
    }

@mcp.tool
def import_users_csv(filename: str, skip_duplicates: bool = True) -> Dict:
    """从CSV文件导入用户数据
    
    Args:
        filename: CSV文件名
        skip_duplicates: 是否跳过重复用户
        
    Returns:
        导入结果统计
        
    Raises:
        ValueError: 文件不存在时
    """
    if not os.path.exists(filename):
        raise ValueError(f"文件 {filename} 不存在")
    
    imported_count = 0
    skipped_count = 0
    error_count = 0
    errors = []
    
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # 验证必需字段
        required_fields = {'username', 'email', 'name'}
        if not required_fields.issubset(set(reader.fieldnames)):
            missing = required_fields - set(reader.fieldnames)
            raise ValueError(f"CSV文件缺少必需字段: {', '.join(missing)}")
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # 数据清理
                username = row['username'].strip()
                email = row['email'].strip()
                name = row['name'].strip()
                
                if not username or not email or not name:
                    errors.append(f"第{row_num}行: 存在空字段")
                    error_count += 1
                    continue
                
                # 尝试创建用户
                create_user(username, email, name)
                imported_count += 1
                
            except ValueError as e:
                if skip_duplicates and ("已存在" in str(e) or "已被使用" in str(e)):
                    skipped_count += 1
                else:
                    error_count += 1
                    errors.append(f"第{row_num}行: {str(e)}")
            except Exception as e:
                error_count += 1
                errors.append(f"第{row_num}行: 未知错误 - {str(e)}")
    
    return {
        "filename": filename,
        "total_processed": imported_count + skipped_count + error_count,
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "error_count": error_count,
        "errors": errors[:10],  # 只返回前10个错误
        "success_rate": f"{(imported_count / (imported_count + error_count) * 100):.1f}%" if (imported_count + error_count) > 0 else "0%",
        "imported_at": datetime.now().isoformat()
    }

# ============================================================================
# 资源：配置和统计信息
# ============================================================================

@mcp.resource("database://config")
def get_db_config() -> Dict:
    """获取数据库配置信息（脱敏）"""
    return {
        "database_type": "SQLite",
        "database_file": "users.db",
        "tables": ["users"],
        "indexes": ["idx_username", "idx_email", "idx_status"],
        "connection_pool": "disabled",
        "last_backup": "2025-01-15 10:30:00",
        "auto_vacuum": "incremental",
        "journal_mode": "WAL"
    }

@mcp.resource("users://stats")
def get_user_stats() -> Dict:
    """获取用户统计信息"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # 总用户数
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # 各状态用户数
    cursor.execute('SELECT status, COUNT(*) FROM users GROUP BY status')
    status_counts = dict(cursor.fetchall())
    
    # 今天新增用户数
    cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE("now")')
    today_new = cursor.fetchone()[0]
    
    # 本月新增用户数
    cursor.execute('SELECT COUNT(*) FROM users WHERE strftime("%Y-%m", created_at) = strftime("%Y-%m", "now")')
    month_new = cursor.fetchone()[0]
    
    # 最近活跃用户（基于updated_at）
    cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(updated_at) >= DATE("now", "-7 days")')
    week_active = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_users": total_users,
        "status_breakdown": status_counts,
        "new_users": {
            "today": today_new,
            "this_month": month_new
        },
        "activity": {
            "active_this_week": week_active
        },
        "health_indicators": {
            "active_ratio": f"{(status_counts.get('active', 0) / total_users * 100):.1f}%" if total_users > 0 else "0%",
            "growth_rate": "稳定增长" if today_new > 0 else "无新增"
        },
        "last_updated": datetime.now().isoformat()
    }

@mcp.resource("help://user-management") 
def get_help_doc() -> str:
    """获取用户管理系统使用说明"""
    return """
# 用户管理系统使用指南

## 查询功能
- **get_user_by_id(user_id)**: 根据ID查询用户信息
- **search_users(keyword, limit)**: 模糊搜索用户（支持用户名、邮箱、姓名）
- **list_users(limit, offset, status)**: 获取用户列表（支持分页和状态筛选）

## 管理功能
- **create_user(username, email, name)**: 创建新用户
- **update_user_status(user_id, status)**: 更新用户状态
- **update_user_info(user_id, name, email)**: 更新用户基本信息

## 通知功能
- **send_welcome_email(user_id)**: 发送欢迎邮件
- **validate_email_domain(email)**: 验证邮箱域名

## 数据管理
- **export_users_csv(status, include_emails)**: 导出用户数据
- **import_users_csv(filename, skip_duplicates)**: 导入用户数据

## 资源信息
- **database://config**: 数据库配置信息
- **users://stats**: 用户统计数据
- **help://user-management**: 本使用说明

## 用户状态说明
- **active**: 正常用户，可正常使用所有功能
- **inactive**: 非活跃用户，账户暂时停用
- **suspended**: 暂停用户，因违规等原因被暂停

## 使用建议
1. 创建用户前建议先验证邮箱域名
2. 定期导出用户数据进行备份
3. 监控用户状态分布，及时处理异常账户
4. 使用搜索功能快速定位特定用户

## 注意事项
- 用户名和邮箱具有唯一性约束
- 用户名需要3个字符以上，只能包含字母、数字和下划线
- 邮箱格式需要符合标准规范
- 删除用户前请确保已备份重要数据
"""

# 启动时初始化数据库
init_database()

if __name__ == "__main__":
    print("👥 用户管理系统启动中...")
    print("=" * 60)
    print("📋 可用工具:")
    print("  🔍 查询: get_user_by_id, search_users, list_users")
    print("  ✏️  管理: create_user, update_user_status, update_user_info")
    print("  📧 通知: send_welcome_email, validate_email_domain")
    print("  📁 数据: export_users_csv, import_users_csv")
    print("\n📚 可用资源:")
    print("  🗃️  database://config - 数据库配置")
    print("  📊 users://stats - 用户统计")
    print("  📖 help://user-management - 使用说明")
    print("\n💡 试试这些命令:")
    print("  '查询用户张三的信息'")
    print("  '创建一个新用户'")
    print("  '获取用户统计数据'")
    print("  '导出所有活跃用户'")
    print("=" * 60)
    print("🛑 使用 Ctrl+C 停止服务器\n")
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\n👥 用户管理系统已停止")