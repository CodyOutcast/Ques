#!/usr/bin/env python3
"""
Intelligent Search Agent - Database Integration Test
Test the integration functionality of vector search and database API
"""

import asyncio
import sys
import time

# Add path
sys.path.append('src/vector_search')
from intelligent_search_agent import SearchAgent


async def test_database_integration():
    """Test database integration functionality"""
    
    print("🚀 Intelligent Search Agent - Database Integration Test")
    print("=" * 60)
    
    # Initialize search agent
    api_key = "9bdbfb8ff9da4f0bbd36dc49ce71d05c.nNSSJqmxu1Z2iZzD"
    api_base_url = "http://localhost:8000"  # Local database API
    
    agent = SearchAgent(
        glm_api_key=api_key,
        api_base_url=api_base_url
    )
    
    # Test queries
    test_queries = [
        "寻找Python工程师，有全栈开发经验",
        "Looking for AI engineer with machine learning experience"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test query {i}/{len(test_queries)}: {query}")
        print("-" * 50)
        
        try:
            # Test complete intelligent search (including database integration)
            start_time = time.time()
            result = await agent.intelligent_search(
                user_query=query,
                user_id="test_user",
                referenced_users=None,
                viewed_user_ids=[]
            )
            total_time = time.time() - start_time
            
            if result.get("status") == "success":
                candidates = result.get("candidates", [])
                print(f"✅ Search successful - found {len(candidates)} candidates")
                print(f"⏱️ Total time: {total_time:.3f} seconds")
                print(f"🌐 Language: {result.get('language')}")
                print(f"🎯 Quality: {result.get('search_quality')}")
                
                # Check candidate data structure
                if candidates:
                    print(f"\n📊 Candidate details check:")
                    for j, candidate in enumerate(candidates[:2], 1):  # Only check first 2
                        print(f"  Candidate {j}:")
                        print(f"    - ID: {candidate.get('id', candidate.get('user_id'))}")
                        print(f"    - Name: {candidate.get('name', 'Unknown')}")
                        print(f"    - Introduction: {candidate.get('one_sentence_intro', 'None')[:50]}...")
                        print(f"    - Skills: {candidate.get('skills', [])[:3]}...")
                        print(f"    - University: {candidate.get('current_university', 'Unknown')}")
                        print(f"    - Match score: {candidate.get('score', 0):.3f}")
                        print(f"    - Match reason: {candidate.get('match_reason', 'None')}")
                        
                        # Check for database errors
                        if candidate.get('error'):
                            print(f"    ⚠️ Database error: {candidate['error']}")
                        else:
                            print(f"    ✅ Database integration successful")
                        print()
                
                # Performance statistics
                perf_stats = result.get("performance_stats", {})
                if perf_stats:
                    print(f"📈 Performance statistics:")
                    print(f"  - Language detection: {perf_stats.get('language_detection', 0):.3f} seconds")
                    print(f"  - Preprocessing: {perf_stats.get('preprocessing', 0):.3f} seconds")
                    
                    vector_searches = perf_stats.get('vector_searches', {})
                    for search_key, search_time in vector_searches.items():
                        print(f"  - Vector search {search_key}: {search_time:.3f} seconds")
                    
                    candidate_analysis = perf_stats.get('candidate_analysis', {})
                    for analysis_key, analysis_time in candidate_analysis.items():
                        print(f"  - Candidate analysis {analysis_key}: {analysis_time:.3f} seconds")
                    
                    print(f"  - Result generation: {perf_stats.get('result_generation', 0):.3f} seconds")
                    print(f"  - Total time: {perf_stats.get('total_time', 0):.3f} seconds")
                
            else:
                print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
        
        # 短暂休息
        if i < len(test_queries):
            await asyncio.sleep(1)
    
    print(f"\n🎉 数据库集成测试完成！")


async def test_hybrid_search_only():
    """仅测试混合搜索功能"""
    
    print("\n🔍 测试混合搜索功能")
    print("=" * 40)
    
    # 初始化搜索代理
    api_key = "9bdbfb8ff9da4f0bbd36dc49ce71d05c.nNSSJqmxu1Z2iZzD"
    api_base_url = "http://localhost:8000"
    
    agent = SearchAgent(
        glm_api_key=api_key,
        api_base_url=api_base_url
    )
    
    query = "寻找Python工程师"
    
    try:
        print(f"查询: {query}")
        
        # 测试混合搜索（包含数据库集成）
        start_time = time.time()
        results = await agent.hybrid_search(
            dense_query=query,
            sparse_query="Python 工程师 开发",
            search_strategy="standard",
            limit=5,
            fetch_db_details=True
        )
        search_time = time.time() - start_time
        
        print(f"✅ 混合搜索完成")
        print(f"⏱️ 搜索耗时: {search_time:.3f}秒")
        print(f"📊 找到候选人: {len(results)}")
        
        if results:
            print(f"\n前3个候选人:")
            for i, candidate in enumerate(results[:3], 1):
                print(f"  {i}. {candidate.get('name', '未知')} - {candidate.get('one_sentence_intro', '无简介')[:30]}...")
                print(f"     匹配度: {candidate.get('score', 0):.3f}")
                if candidate.get('error'):
                    print(f"     ⚠️ 数据库错误: {candidate['error']}")
        
    except Exception as e:
        print(f"❌ 混合搜索测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 检查数据库API是否可访问
    print("🔗 检查数据库API连接...")
    try:
        import httpx
        import asyncio
        
        async def check_api():
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:8000/health")
                if response.status_code == 200:
                    print("✅ 数据库API连接正常")
                    data = response.json()
                    print(f"   用户数量: {data.get('user_count', 0)}")
                    return True
                else:
                    print(f"❌ 数据库API响应异常: {response.status_code}")
                    return False
        
        api_ok = asyncio.run(check_api())
        
        if api_ok:
            # 运行数据库集成测试
            asyncio.run(test_database_integration())
            
            # 运行混合搜索测试
            asyncio.run(test_hybrid_search_only())
        else:
            print("⚠️ 请确保数据库API服务正在运行:")
            print("   cd /Users/jimmy/Desktop/quesai_backend_test")
            print("   python src/api/main.py")
    
    except ImportError:
        print("❌ 缺少 httpx 依赖，请安装: pip install httpx")
    except Exception as e:
        print(f"❌ API连接检查失败: {e}")
        print("⚠️ 请确保数据库API服务正在运行")