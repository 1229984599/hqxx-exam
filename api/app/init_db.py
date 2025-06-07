"""
初始化数据库脚本
创建默认管理员和基础数据
"""
import asyncio
from tortoise import Tortoise
from app.config import TORTOISE_ORM
from app.models.admin import Admin
from app.models.semester import Semester
from app.models.grade import Grade
from app.models.subject import Subject
from app.utils.auth import get_password_hash


async def init_db():
    """初始化数据库"""
    # 初始化Tortoise ORM
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 生成数据库表
    await Tortoise.generate_schemas()
    
    # 创建默认超级管理员
    admin_exists = await Admin.filter(username="admin").exists()
    if not admin_exists:
        await Admin.create(
            username="admin",
            email="admin@hqxx.edu.cn",
            hashed_password=get_password_hash("admin123"),
            full_name="系统管理员",
            is_active=True,
            is_superuser=True
        )
        print("✅ 创建默认管理员: admin / admin123")
    
    # 创建默认学期
    semester_exists = await Semester.exists()
    if not semester_exists:
        semesters = [
            {"name": "2024年春季学期", "code": "2024S", "sort_order": 1},
            {"name": "2024年秋季学期", "code": "2024F", "sort_order": 2},
        ]
        for semester_data in semesters:
            await Semester.create(**semester_data)
        print("✅ 创建默认学期数据")
    
    # 创建默认年级
    grade_exists = await Grade.exists()
    if not grade_exists:
        grades = [
            {"name": "一年级", "code": "G1", "level": 1, "sort_order": 1},
            {"name": "二年级", "code": "G2", "level": 2, "sort_order": 2},
            {"name": "三年级", "code": "G3", "level": 3, "sort_order": 3},
            {"name": "四年级", "code": "G4", "level": 4, "sort_order": 4},
            {"name": "五年级", "code": "G5", "level": 5, "sort_order": 5},
            {"name": "六年级", "code": "G6", "level": 6, "sort_order": 6},
        ]
        for grade_data in grades:
            await Grade.create(**grade_data)
        print("✅ 创建默认年级数据")
    
    # 创建默认学科
    subject_exists = await Subject.exists()
    if not subject_exists:
        subjects = [
            {"name": "语文", "code": "chinese", "color": "#ff6b6b", "sort_order": 1},
            {"name": "数学", "code": "math", "color": "#4ecdc4", "sort_order": 2},
            {"name": "英语", "code": "english", "color": "#45b7d1", "sort_order": 3},
            {"name": "科学", "code": "science", "color": "#96ceb4", "sort_order": 4},
            {"name": "道德与法治", "code": "moral", "color": "#feca57", "sort_order": 5},
        ]
        for subject_data in subjects:
            await Subject.create(**subject_data)
        print("✅ 创建默认学科数据")
    
    # 创建默认分类
    from app.models.category import Category
    category_exists = await Category.exists()
    if not category_exists:
        # 获取学科
        chinese = await Subject.filter(code="chinese").first()
        math = await Subject.filter(code="math").first()

        if chinese:
            categories_data = [
                {"name": "拼音", "code": "pinyin", "subject_id": chinese.id, "sort_order": 1},
                {"name": "识字", "code": "words", "subject_id": chinese.id, "sort_order": 2},
                {"name": "阅读理解", "code": "reading", "subject_id": chinese.id, "sort_order": 3},
            ]
            for cat_data in categories_data:
                await Category.create(**cat_data)

        if math:
            categories_data = [
                {"name": "加减法", "code": "addition", "subject_id": math.id, "sort_order": 1},
                {"name": "乘除法", "code": "multiplication", "subject_id": math.id, "sort_order": 2},
                {"name": "应用题", "code": "word_problems", "subject_id": math.id, "sort_order": 3},
            ]
            for cat_data in categories_data:
                await Category.create(**cat_data)

        print("✅ 创建默认分类数据")

    # 创建测试题目
    from app.models.question import Question
    question_exists = await Question.exists()
    if not question_exists:
        # 获取基础数据
        semester = await Semester.filter(code="2024S").first()
        grade = await Grade.filter(code="G1").first()
        chinese = await Subject.filter(code="chinese").first()
        math = await Subject.filter(code="math").first()

        if semester and grade and chinese and math:
            # 获取分类
            pinyin_cat = await Category.filter(code="pinyin").first()
            addition_cat = await Category.filter(code="addition").first()

            if pinyin_cat:
                questions_data = [
                    {
                        "title": "拼音练习：声母b",
                        "content": "<p>请读出下面的拼音：<br><strong>ba  bi  bu  bo</strong></p>",
                        "answer": "ba读作巴，bi读作比，bu读作不，bo读作波",
                        "difficulty": 1,
                        "semester_id": semester.id,
                        "grade_id": grade.id,
                        "subject_id": chinese.id,
                        "category_id": pinyin_cat.id,
                        "is_published": True
                    },
                    {
                        "title": "拼音练习：韵母a",
                        "content": "<p>请读出下面的拼音：<br><strong>ma  fa  la  da</strong></p>",
                        "answer": "ma读作妈，fa读作发，la读作拉，da读作大",
                        "difficulty": 1,
                        "semester_id": semester.id,
                        "grade_id": grade.id,
                        "subject_id": chinese.id,
                        "category_id": pinyin_cat.id,
                        "is_published": True
                    }
                ]
                for q_data in questions_data:
                    await Question.create(**q_data)

            if addition_cat:
                questions_data = [
                    {
                        "title": "10以内加法：5+3",
                        "content": "<p>计算下面的加法题：</p><h2>5 + 3 = ?</h2>",
                        "answer": "8",
                        "explanation": "5个苹果加上3个苹果，一共是8个苹果",
                        "difficulty": 1,
                        "semester_id": semester.id,
                        "grade_id": grade.id,
                        "subject_id": math.id,
                        "category_id": addition_cat.id,
                        "is_published": True
                    },
                    {
                        "title": "10以内加法：7+2",
                        "content": "<p>计算下面的加法题：</p><h2>7 + 2 = ?</h2>",
                        "answer": "9",
                        "explanation": "7个玩具加上2个玩具，一共是9个玩具",
                        "difficulty": 1,
                        "semester_id": semester.id,
                        "grade_id": grade.id,
                        "subject_id": math.id,
                        "category_id": addition_cat.id,
                        "is_published": True
                    }
                ]
                for q_data in questions_data:
                    await Question.create(**q_data)

        print("✅ 创建测试题目数据")

    print("🎉 数据库初始化完成!")

    # 关闭连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_db())
