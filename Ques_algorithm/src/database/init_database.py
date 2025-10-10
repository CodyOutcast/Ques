#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database initialization script
Creates SQLite database and all related table structures
"""

import sqlite3
import json
from datetime import datetime, date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_FILE = "quesai_test.db"

def create_database():
    """Create database and all table structures"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 1. Create users table
        create_users_table(cursor)
        
        # 2. Create provinces table
        create_provinces_table(cursor)
        
        # 3. Create cities table  
        create_cities_table(cursor)
        
        # 4. Create institutions table
        create_institutions_table(cursor)
        
        # 5. Create user profiles table
        create_user_profiles_table(cursor)
        
        # 6. Create user projects table
        create_user_projects_table(cursor)
        
        # 7. Create user institutions association table
        create_user_institutions_table(cursor)
        
        # 8. Insert basic geographic data
        insert_basic_location_data(cursor)
        
        # 9. Insert basic institution data
        insert_basic_institution_data(cursor)
        
        conn.commit()
        logger.info("Database created successfully!")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Database creation failed: {e}")
        raise
    finally:
        conn.close()

def create_users_table(cursor):
    """Create users table"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            openid VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(100) NULL,
            phone VARCHAR(20) NULL,
            email VARCHAR(200) NULL,
            user_status TEXT DEFAULT 'active' CHECK (user_status IN ('active', 'inactive', 'suspended')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(user_status)")
    
    logger.info("Users table created successfully")

def create_provinces_table(cursor):
    """Create provinces table"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS provinces (
            id INTEGER PRIMARY KEY,
            name_en VARCHAR(100) NOT NULL,
            name_cn VARCHAR(100) NOT NULL
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_provinces_name_en ON provinces(name_en)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_provinces_name_cn ON provinces(name_cn)")
    
    logger.info("Provinces table created successfully")

def create_cities_table(cursor):
    """Create cities table"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY,
            province_id INTEGER NOT NULL,
            name_en VARCHAR(100) NOT NULL,
            name_cn VARCHAR(100) NOT NULL,
            FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cities_province_id ON cities(province_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cities_name_en ON cities(name_en)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cities_name_cn ON cities(name_cn)")
    
    logger.info("Cities table created successfully")

def create_institutions_table(cursor):
    """Create institutions table"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS institutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            name_en VARCHAR(200) NULL,
            type TEXT NOT NULL CHECK (type IN ('university', 'company', 'research', 'government', 'ngo', 'other')),
            description TEXT NULL,
            location VARCHAR(200) NULL,
            website VARCHAR(500) NULL,
            logo_url TEXT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_institutions_name ON institutions(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_institutions_type ON institutions(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_institutions_location ON institutions(location)")
    
    logger.info("Institutions table created successfully")

def create_user_profiles_table(cursor):
    """Create user profiles table"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            age INTEGER NULL,
            birthday DATE NULL,
            gender TEXT NULL CHECK (gender IN ('男', '女', '其他')),
            province_id INTEGER NULL,
            city_id INTEGER NULL,
            province_name_cn VARCHAR(100) NULL,
            city_name_cn VARCHAR(100) NULL,
            location VARCHAR(200) NULL,
            profile_photo TEXT NULL,
            one_sentence_intro TEXT NULL,
            hobbies TEXT NULL,  -- JSON string
            languages TEXT NULL,  -- JSON string
            skills TEXT NULL,  -- JSON string
            resources TEXT NULL,  -- JSON string
            goals TEXT NULL,
            demands TEXT NULL,  -- JSON string
            current_university VARCHAR(200) NULL,
            university_email VARCHAR(200) NULL,
            university_verified BOOLEAN DEFAULT 0,
            wechat_id VARCHAR(100) NULL,
            wechat_verified BOOLEAN DEFAULT 0,
            is_profile_complete BOOLEAN DEFAULT 0,
            profile_visibility TEXT DEFAULT 'public',
            project_count INTEGER DEFAULT 0,
            institution_count INTEGER DEFAULT 0,
            last_active TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE SET NULL,
            FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE SET NULL
        )
    """)
    
    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_location ON user_profiles(location)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_province ON user_profiles(province_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_city ON user_profiles(city_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_age ON user_profiles(age)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_birthday ON user_profiles(birthday)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_gender ON user_profiles(gender)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_visibility ON user_profiles(profile_visibility)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_project_count ON user_profiles(project_count DESC)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_institution_count ON user_profiles(institution_count DESC)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_last_active ON user_profiles(last_active)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_university ON user_profiles(current_university)",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_complete ON user_profiles(is_profile_complete)"
    ]
    
    for index in indexes:
        cursor.execute(index)
    
    logger.info("User profiles table created successfully")

def create_user_projects_table(cursor):
    """Create user projects table"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT NULL,
            role VARCHAR(100) NULL,
            start_date DATE NULL,
            end_date DATE NULL,
            is_current BOOLEAN DEFAULT 0,
            skills_used TEXT NULL,  -- JSON string
            reference_links TEXT NULL,  -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_projects_user_id ON user_projects(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_projects_title ON user_projects(title)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_projects_current ON user_projects(user_id, is_current)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_projects_dates ON user_projects(start_date, end_date)")
    
    logger.info("User projects table created successfully")

def create_user_institutions_table(cursor):
    """Create user institutions association table"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_institutions (
            user_id INTEGER NOT NULL,
            institution_id INTEGER NOT NULL,
            role VARCHAR(100) NULL,
            position VARCHAR(100) NULL,
            department VARCHAR(100) NULL,
            start_date DATE NULL,
            end_date DATE NULL,
            is_current BOOLEAN DEFAULT 1,
            description TEXT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, institution_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_institutions_user_id ON user_institutions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_institutions_institution_id ON user_institutions(institution_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_institutions_current ON user_institutions(user_id, is_current)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_institutions_dates ON user_institutions(start_date, end_date)")
    
    logger.info("User institutions association table created successfully")

def insert_basic_location_data(cursor):
    """Insert basic geographic location data"""
    # Insert major provinces
    provinces = [
        (1, 'Beijing', '北京市'),
        (2, 'Shanghai', '上海市'),
        (3, 'Guangdong', '广东省'),
        (4, 'Zhejiang', '浙江省'),
        (5, 'Jiangsu', '江苏省'),
        (6, 'Sichuan', '四川省'),
        (7, 'Shandong', '山东省'),
        (8, 'Hubei', '湖北省'),
        (9, 'Hunan', '湖南省'),
        (10, 'Fujian', '福建省'),
        (11, 'Tianjin', '天津市'),
        (12, 'Chongqing', '重庆市'),
        (13, 'Liaoning', '辽宁省'),
        (14, 'Jilin', '吉林省'),
        (15, 'Heilongjiang', '黑龙江省')
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO provinces (id, name_en, name_cn) VALUES (?, ?, ?)", provinces)
    
    # Insert major cities
    cities = [
        (101, 1, 'Haidian', '海淀区'),
        (102, 1, 'Chaoyang', '朝阳区'),
        (103, 1, 'Dongcheng', '东城区'),
        (104, 1, 'Xicheng', '西城区'),
        (201, 2, 'Pudong', '浦东新区'),
        (202, 2, 'Huangpu', '黄浦区'),
        (203, 2, 'Xuhui', '徐汇区'),
        (301, 3, 'Guangzhou', '广州市'),
        (302, 3, 'Shenzhen', '深圳市'),
        (303, 3, 'Dongguan', '东莞市'),
        (401, 4, 'Hangzhou', '杭州市'),
        (402, 4, 'Ningbo', '宁波市'),
        (501, 5, 'Nanjing', '南京市'),
        (502, 5, 'Suzhou', '苏州市'),
        (601, 6, 'Chengdu', '成都市'),
        (701, 7, 'Jinan', '济南市'),
        (702, 7, 'Qingdao', '青岛市'),
        (801, 8, 'Wuhan', '武汉市'),
        (901, 9, 'Changsha', '长沙市'),
        (1001, 10, 'Fuzhou', '福州市'),
        (1002, 10, 'Xiamen', '厦门市')
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO cities (id, province_id, name_en, name_cn) VALUES (?, ?, ?, ?)", cities)
    
    logger.info("Basic geographic location data inserted successfully")

def insert_basic_institution_data(cursor):
    """Insert basic institution data"""
    institutions = [
        # 大学
        ('清华大学', 'Tsinghua University', 'university', '中国顶尖理工科大学', '北京市海淀区', 'https://www.tsinghua.edu.cn', None),
        ('北京大学', 'Peking University', 'university', '中国顶尖综合性大学', '北京市海淀区', 'https://www.pku.edu.cn', None),
        ('复旦大学', 'Fudan University', 'university', '中国顶尖综合性大学', '上海市杨浦区', 'https://www.fudan.edu.cn', None),
        ('上海交通大学', 'Shanghai Jiao Tong University', 'university', '中国顶尖理工科大学', '上海市闵行区', 'https://www.sjtu.edu.cn', None),
        ('浙江大学', 'Zhejiang University', 'university', '中国顶尖综合性大学', '浙江省杭州市', 'https://www.zju.edu.cn', None),
        ('南京大学', 'Nanjing University', 'university', '中国顶尖综合性大学', '江苏省南京市', 'https://www.nju.edu.cn', None),
        ('中山大学', 'Sun Yat-sen University', 'university', '中国著名综合性大学', '广东省广州市', 'https://www.sysu.edu.cn', None),
        ('华中科技大学', 'Huazhong University of Science and Technology', 'university', '中国著名理工科大学', '湖北省武汉市', 'https://www.hust.edu.cn', None),
        
        # 知名公司
        ('阿里巴巴集团', 'Alibaba Group', 'company', '中国最大的电商和云计算公司', '浙江省杭州市', 'https://www.alibaba.com', None),
        ('腾讯', 'Tencent', 'company', '中国最大的互联网公司之一', '广东省深圳市', 'https://www.tencent.com', None),
        ('百度', 'Baidu', 'company', '中国最大的搜索引擎公司', '北京市海淀区', 'https://www.baidu.com', None),
        ('字节跳动', 'ByteDance', 'company', '全球化的移动互联网公司', '北京市海淀区', 'https://www.bytedance.com', None),
        ('华为技术有限公司', 'Huawei Technologies', 'company', '全球领先的ICT基础设施和智能终端提供商', '广东省深圳市', 'https://www.huawei.com', None),
        ('小米科技', 'Xiaomi Corporation', 'company', '以手机、智能硬件和IoT平台为核心的互联网公司', '北京市海淀区', 'https://www.mi.com', None),
        ('美团', 'Meituan', 'company', '中国领先的生活服务电子商务平台', '北京市朝阳区', 'https://www.meituan.com', None),
        ('滴滴出行', 'Didi Chuxing', 'company', '全球领先的移动出行平台', '北京市海淀区', 'https://www.didiglobal.com', None),
        ('京东', 'JD.com', 'company', '中国领先的技术驱动的电商和零售基础设施服务商', '北京市亦庄经济技术开发区', 'https://www.jd.com', None),
        ('网易', 'NetEase', 'company', '中国领先的互联网技术公司', '浙江省杭州市', 'https://www.163.com', None)
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO institutions (name, name_en, type, description, location, website, logo_url) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, institutions)
    
    logger.info("Basic institution data inserted successfully")

if __name__ == "__main__":
    create_database()
    print(f"Database file created: {DB_FILE}")