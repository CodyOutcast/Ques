#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据生成脚本
生成1000条多样化的用户数据用于搜索功能测试
"""

import sqlite3
import json
import random
from datetime import datetime, date, timedelta
from faker import Faker
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化Faker
fake = Faker(['zh_CN', 'en_US'])
Faker.seed(42)  # 设置随机种子保证可重现

DB_FILE = "quesai_test.db"

# 技能池
SKILLS_POOL = {
    'programming': ['Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB'],
    'web': ['React', 'Vue.js', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring Boot', 'Express.js', 'Laravel', 'Rails'],
    'mobile': ['iOS开发', 'Android开发', 'React Native', 'Flutter', 'Xamarin', '小程序开发', 'Ionic'],
    'data': ['机器学习', '深度学习', '数据分析', '数据挖掘', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn', 'Spark'],
    'database': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server', 'Elasticsearch', 'InfluxDB'],
    'cloud': ['AWS', 'Azure', 'Google Cloud', '阿里云', '腾讯云', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI'],
    'design': ['UI设计', 'UX设计', 'Photoshop', 'Sketch', 'Figma', 'Adobe XD', '产品设计', '交互设计'],
    'business': ['产品管理', '项目管理', '数字营销', '内容营销', 'SEO', 'SEM', '商业分析', '战略规划'],
    'language': ['英语', '日语', '韩语', '德语', '法语', '西班牙语', '俄语', '阿拉伯语']
}

# 兴趣爱好池
HOBBIES_POOL = [
    '编程', '阅读', '健身', '跑步', '游泳', '篮球', '足球', '羽毛球', '乒乓球', '网球',
    '摄影', '旅行', '美食', '电影', '音乐', '绘画', '书法', '瑜伽', '登山', '骑行',
    '烹饪', '园艺', '钢琴', '吉他', '小提琴', '舞蹈', '唱歌', '写作', '博客', '播客',
    '游戏', '桌游', '收藏', '手工', '茶艺', '咖啡', '红酒', '化妆', '时尚', '购物'
]

# 资源池
RESOURCES_POOL = [
    'Python教程', 'Java项目经验', '机器学习算法', '前端开发资源', '产品设计经验',
    '创业经验', '投资经验', '团队管理经验', '市场营销经验', '财务管理知识',
    '法律咨询', '人力资源经验', '技术培训', '行业人脉', '供应链资源',
    '媒体资源', '政府关系', '国际贸易经验', '品牌建设经验', '融资渠道'
]

# 需求池
DEMANDS_POOL = [
    '寻找技术合伙人', '需要前端开发资源', '寻找投资机会', '需要市场推广建议',
    '寻找产品经理', '需要UI设计师', '寻找运营人才', '需要法律咨询',
    '寻找供应商', '需要融资支持', '寻找导师', '需要创业伙伴',
    '寻找客户资源', '需要技术指导', '寻找行业专家', '需要人才招聘'
]

# 目标模板
GOALS_TEMPLATES = [
    "希望在{field}领域深入发展，成为{role}，带领团队开发创新的{product}解决方案",
    "致力于成为{field}专家，通过{skill}技术推动行业发展，实现{vision}",
    "目标是建立自己的{company_type}，专注于{area}，为用户提供{value}",
    "想要在{industry}行业发挥专长，担任{position}，推动{innovation}的发展",
    "希望通过{method}方式，在{timeline}内实现{goal}，成为{field}的领军人物"
]

# 一句话介绍模板
INTRO_TEMPLATES = [
    "{trait}的{role}，专注于{field}{focus}",
    "{experience}年{field}经验的{role}，{specialty}专家",
    "热爱{interest}的{role}，致力于{mission}",
    "{background}背景的{role}，擅长{skill}和{area}",
    "有着{trait}和{quality}的{role}，专业领域是{field}"
]

def generate_test_data():
    """生成1000条测试用户数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # 获取省市和机构数据
        provinces, cities, institutions = get_reference_data(cursor)
        
        logger.info("开始生成1000条用户数据...")
        
        for i in range(1000):
            if i % 100 == 0:
                logger.info(f"已生成 {i} 条用户数据...")
            
            user_data = generate_single_user(i + 1, provinces, cities, institutions)
            insert_user_data(cursor, user_data)
        
        conn.commit()
        logger.info("所有用户数据生成完成！")
        
        # 更新统计字段
        update_statistics(cursor)
        conn.commit()
        
        logger.info("统计字段更新完成！")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"数据生成失败: {e}")
        raise
    finally:
        conn.close()

def get_reference_data(cursor):
    """获取参考数据"""
    # 获取省份数据
    cursor.execute("SELECT id, name_cn FROM provinces")
    provinces = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 获取城市数据
    cursor.execute("SELECT id, province_id, name_cn FROM cities")
    cities = {}
    for city_id, province_id, name in cursor.fetchall():
        if province_id not in cities:
            cities[province_id] = []
        cities[province_id].append((city_id, name))
    
    # 获取机构数据
    cursor.execute("SELECT id, name, type FROM institutions")
    institutions = cursor.fetchall()
    
    return provinces, cities, institutions

def generate_single_user(user_id, provinces, cities, institutions):
    """生成单个用户数据"""
    # 基础信息
    name = fake.name()
    age = random.randint(22, 45)
    birthday = date.today() - timedelta(days=age * 365 + random.randint(0, 365))
    gender = random.choice(['男', '女'])
    
    # 地理位置
    province_id = random.choice(list(provinces.keys()))
    province_name = provinces[province_id]
    
    city_data = random.choice(cities.get(province_id, [(101, '海淀区')]))
    city_id, city_name = city_data
    location = f"{province_name}{city_name}"
    
    # 技能生成
    skills = generate_skills()
    
    # 兴趣爱好
    hobbies = random.sample(HOBBIES_POOL, random.randint(3, 8))
    
    # 语言能力
    languages = ['中文']
    if random.random() < 0.8:
        languages.append('英语')
    if random.random() < 0.3:
        languages.extend(random.sample(['日语', '韩语', '德语', '法语'], random.randint(1, 2)))
    
    # 资源和需求
    resources = random.sample(RESOURCES_POOL, random.randint(2, 5))
    demands = random.sample(DEMANDS_POOL, random.randint(1, 4))
    
    # 大学信息
    university_institutions = [inst for inst in institutions if inst[2] == 'university']
    current_university = random.choice(university_institutions)[1] if random.random() < 0.7 else None
    
    # 生成目标
    goals = generate_goals(skills)
    
    # 生成一句话介绍
    intro = generate_intro(skills, age)
    
    # 项目数量
    project_count = random.randint(1, 5)
    
    # 机构数量
    institution_count = random.randint(1, 3)
    
    user_data = {
        'id': user_id,
        'name': name,
        'age': age,
        'birthday': birthday,
        'gender': gender,
        'province_id': province_id,
        'city_id': city_id,
        'province_name_cn': province_name,
        'city_name_cn': city_name,
        'location': location,
        'skills': skills,
        'hobbies': hobbies,
        'languages': languages,
        'resources': resources,
        'demands': demands,
        'current_university': current_university,
        'goals': goals,
        'one_sentence_intro': intro,
        'project_count': project_count,
        'institution_count': institution_count,
        'projects': generate_projects(project_count, skills),
        'institutions': generate_user_institutions(institution_count, institutions, current_university)
    }
    
    return user_data

def generate_skills():
    """生成技能组合"""
    # 选择主要技能域
    primary_domain = random.choice(list(SKILLS_POOL.keys()))
    skills = random.sample(SKILLS_POOL[primary_domain], random.randint(2, 4))
    
    # 添加其他领域的技能
    other_domains = [k for k in SKILLS_POOL.keys() if k != primary_domain]
    for domain in random.sample(other_domains, random.randint(1, 3)):
        skills.extend(random.sample(SKILLS_POOL[domain], random.randint(1, 2)))
    
    return skills[:8]  # 限制技能数量

def generate_goals(skills):
    """生成个人目标"""
    template = random.choice(GOALS_TEMPLATES)
    
    # 根据技能确定领域
    if any(skill in SKILLS_POOL['programming'] + SKILLS_POOL['web'] + SKILLS_POOL['mobile'] for skill in skills):
        field = '技术'
        role = random.choice(['技术专家', '架构师', 'CTO', '技术总监'])
        product = random.choice(['软件', '应用', '平台', '系统'])
    elif any(skill in SKILLS_POOL['data'] for skill in skills):
        field = 'AI'
        role = random.choice(['数据科学家', '算法专家', 'AI产品经理'])
        product = random.choice(['AI产品', '智能系统', '机器学习'])
    elif any(skill in SKILLS_POOL['design'] for skill in skills):
        field = '设计'
        role = random.choice(['设计专家', '创意总监', '用户体验专家'])
        product = random.choice(['设计', '用户体验', '产品'])
    else:
        field = '商业'
        role = random.choice(['产品专家', '商业领袖', '创业者'])
        product = random.choice(['商业', '产品', '服务'])
    
    return template.format(
        field=field,
        role=role,
        product=product,
        skill=random.choice(skills),
        vision=random.choice(['数字化转型', '技术创新', '用户价值', '行业变革']),
        company_type=random.choice(['科技公司', '创业公司', '咨询公司']),
        area=random.choice(['人工智能', '大数据', '云计算', '物联网']),
        value=random.choice(['优质体验', '创新解决方案', '高效服务']),
        industry=random.choice(['互联网', '金融科技', '教育科技', '医疗科技']),
        position=random.choice(['技术负责人', '产品总监', '创新专家']),
        innovation=random.choice(['技术创新', '产品创新', '业务创新']),
        method=random.choice(['技术驱动', '产品驱动', '数据驱动']),
        timeline=random.choice(['3年', '5年', '10年']),
        goal=random.choice(['技术突破', '市场领先', '行业认可'])
    )

def generate_intro(skills, age):
    """生成一句话介绍"""
    template = random.choice(INTRO_TEMPLATES)
    
    # 根据年龄和技能生成特征
    if age < 26:
        trait = random.choice(['年轻有为', '充满活力', '富有创新精神'])
        experience = random.randint(1, 3)
    elif age < 35:
        trait = random.choice(['经验丰富', '专业可靠', '目标明确'])
        experience = random.randint(3, 8)
    else:
        trait = random.choice(['资深专业', '行业专家', '领导力强'])
        experience = random.randint(8, 15)
    
    # 确定角色
    if any(skill in SKILLS_POOL['programming'] + SKILLS_POOL['web'] for skill in skills):
        role = random.choice(['软件工程师', '全栈开发者', '技术专家'])
        field = random.choice(['软件开发', 'Web开发', '技术创新'])
    elif any(skill in SKILLS_POOL['data'] for skill in skills):
        role = random.choice(['数据分析师', '算法工程师', 'AI专家'])
        field = random.choice(['数据科学', '人工智能', '机器学习'])
    elif any(skill in SKILLS_POOL['design'] for skill in skills):
        role = random.choice(['UI设计师', 'UX设计师', '产品设计师'])
        field = random.choice(['用户体验', '产品设计', '视觉设计'])
    else:
        role = random.choice(['产品经理', '项目经理', '商业分析师'])
        field = random.choice(['产品管理', '项目管理', '商业分析'])
    
    return template.format(
        trait=trait,
        role=role,
        field=field,
        focus=random.choice(['创新', '优化', '发展']),
        experience=experience,
        specialty=random.choice(['技术', '产品', '用户体验', '数据']),
        interest=random.choice(skills[:2]),
        mission=random.choice(['技术创新', '用户价值', '产品优化']),
        background=random.choice(['技术', '产品', '设计', '商业']),
        skill=random.choice(skills[:2]),
        area=random.choice(['项目管理', '团队协作', '创新思维']),
        quality=random.choice(['责任心', '执行力', '创新能力'])
    )

def generate_projects(project_count, skills):
    """生成项目经历"""
    projects = []
    
    project_titles = [
        '智能推荐系统', '电商平台', '移动应用开发', '数据分析平台', '企业管理系统',
        '社交网络应用', '在线教育平台', '金融科技产品', '物联网解决方案', '区块链应用',
        '人工智能助手', '大数据处理平台', '云计算服务', '游戏开发项目', '医疗信息系统'
    ]
    
    roles = [
        '项目负责人', '技术负责人', '产品经理', '架构师', '开发工程师',
        '数据分析师', '算法工程师', '前端工程师', '后端工程师', '全栈工程师'
    ]
    
    for i in range(project_count):
        title = random.choice(project_titles)
        role = random.choice(roles)
        
        # 生成项目描述
        descriptions = [
            f"基于{random.choice(skills[:3])}技术开发的{title.lower()}，提升用户体验{random.randint(20, 50)}%",
            f"使用{random.choice(skills[:3])}和{random.choice(skills[:3])}构建的{title.lower()}，日处理量达{random.randint(10, 1000)}万次",
            f"负责{title.lower()}的{random.choice(['架构设计', '核心开发', '产品规划'])}，团队规模{random.randint(3, 15)}人"
        ]
        
        # 项目时间
        start_date = fake.date_between(start_date='-3y', end_date='-1m')
        is_current = random.random() < 0.2
        end_date = None if is_current else fake.date_between(start_date=start_date, end_date='today')
        
        projects.append({
            'title': title,
            'role': role,
            'description': random.choice(descriptions),
            'start_date': start_date,
            'end_date': end_date,
            'is_current': is_current,
            'skills_used': random.sample(skills, min(len(skills), random.randint(2, 5))),
            'reference_links': [fake.url() for _ in range(random.randint(0, 2))]
        })
    
    return projects

def generate_user_institutions(institution_count, institutions, current_university):
    """生成用户机构关联"""
    user_institutions = []
    used_institution_ids = set()
    
    # 教育经历
    if current_university:
        university_inst = next((inst for inst in institutions if inst[1] == current_university), None)
        if university_inst:
            used_institution_ids.add(university_inst[0])
            user_institutions.append({
                'institution_id': university_inst[0],
                'role': random.choice(['本科生', '研究生', '博士生']),
                'position': random.choice(['学士', '硕士', '博士']),
                'department': random.choice(['计算机科学与技术系', '软件学院', '商学院', '管理学院']),
                'start_date': fake.date_between(start_date='-8y', end_date='-4y'),
                'end_date': fake.date_between(start_date='-4y', end_date='-1y'),
                'is_current': False
            })
    
    # 工作经历
    company_institutions = [inst for inst in institutions if inst[2] == 'company']
    work_count = institution_count - (1 if current_university else 0)
    
    # 确保不重复选择机构
    available_companies = [inst for inst in company_institutions if inst[0] not in used_institution_ids]
    
    for i in range(min(work_count, len(available_companies))):
        inst = random.choice(available_companies)
        used_institution_ids.add(inst[0])
        available_companies = [inst for inst in available_companies if inst[0] not in used_institution_ids]
        
        positions = [
            '软件工程师', '高级工程师', '技术专家', '产品经理', '项目经理',
            '数据分析师', '算法工程师', '前端开发', '后端开发', '全栈工程师'
        ]
        
        departments = [
            '技术部', '产品部', '研发中心', 'AI实验室', '数据部门',
            '架构部', '前端组', '后端组', '算法组', '产品组'
        ]
        
        start_date = fake.date_between(start_date='-5y', end_date='-6m')
        is_current = i == 0 and random.random() < 0.6  # 第一个工作更可能是当前工作
        end_date = None if is_current else fake.date_between(start_date=start_date, end_date='today')
        
        user_institutions.append({
            'institution_id': inst[0],
            'role': random.choice(['员工', '工程师', '专家', '管理者']),
            'position': random.choice(positions),
            'department': random.choice(departments),
            'start_date': start_date,
            'end_date': end_date,
            'is_current': is_current,
            'description': f"负责{random.choice(['技术研发', '产品开发', '架构设计', '团队管理'])}工作"
        })
    
    return user_institutions

def insert_user_data(cursor, user_data):
    """插入用户数据到数据库"""
    # 插入用户基础信息
    cursor.execute("""
        INSERT INTO users (openid, name, user_status, created_at, updated_at)
        VALUES (?, ?, 'active', datetime('now'), datetime('now'))
    """, (f"test_user_{user_data['id']}", user_data['name']))
    
    user_id = cursor.lastrowid
    
    # 插入用户档案
    cursor.execute("""
        INSERT INTO user_profiles (
            user_id, age, birthday, gender, province_id, city_id, 
            province_name_cn, city_name_cn, location, profile_photo,
            one_sentence_intro, hobbies, languages, skills, resources,
            goals, demands, current_university, university_verified,
            wechat_verified, is_profile_complete, profile_visibility,
            project_count, institution_count, last_active,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        user_id, user_data['age'], user_data['birthday'], user_data['gender'],
        user_data['province_id'], user_data['city_id'], user_data['province_name_cn'],
        user_data['city_name_cn'], user_data['location'], fake.image_url(),
        user_data['one_sentence_intro'], json.dumps(user_data['hobbies'], ensure_ascii=False),
        json.dumps(user_data['languages'], ensure_ascii=False), 
        json.dumps(user_data['skills'], ensure_ascii=False),
        json.dumps(user_data['resources'], ensure_ascii=False), user_data['goals'],
        json.dumps(user_data['demands'], ensure_ascii=False), user_data['current_university'],
        random.choice([True, False]), random.choice([True, False]), True, 'public',
        user_data['project_count'], user_data['institution_count'],
        fake.date_time_between(start_date='-30d', end_date='now')
    ))
    
    # 插入项目数据
    for i, project in enumerate(user_data['projects']):
        cursor.execute("""
            INSERT INTO user_projects (
                user_id, title, description, role, start_date, end_date,
                is_current, skills_used, reference_links,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            user_id, project['title'], project['description'], project['role'],
            project['start_date'], project['end_date'], project['is_current'],
            json.dumps(project['skills_used'], ensure_ascii=False),
            json.dumps(project['reference_links'], ensure_ascii=False)
        ))
    
    # 插入机构关联数据
    for inst in user_data['institutions']:
        cursor.execute("""
            INSERT INTO user_institutions (
                user_id, institution_id, role, position, department,
                start_date, end_date, is_current, description,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            user_id, inst['institution_id'], inst['role'], inst['position'],
            inst['department'], inst['start_date'], inst['end_date'],
            inst['is_current'], inst.get('description')
        ))

def update_statistics(cursor):
    """更新统计字段"""
    # 更新项目统计
    cursor.execute("""
        UPDATE user_profiles 
        SET project_count = (
            SELECT COUNT(*) 
            FROM user_projects 
            WHERE user_projects.user_id = user_profiles.user_id
        )
    """)
    
    # 更新机构统计
    cursor.execute("""
        UPDATE user_profiles 
        SET institution_count = (
            SELECT COUNT(*) 
            FROM user_institutions 
            WHERE user_institutions.user_id = user_profiles.user_id
        )
    """)

if __name__ == "__main__":
    generate_test_data()
    print("1000条测试用户数据生成完成！")