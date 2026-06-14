"""
主程序入口 - 爬虫使用示例
"""
import logging
import json
from spiders.ecommerce_spider import PddSpider
from utils.storage import get_storage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主程序"""
    
    logger.info('='*50)
    logger.info('电商数据爬虫 - 开始运行')
    logger.info('='*50)
    
    # 创建爬虫实例
    spider = PddSpider()
    
    try:
        # 搜索商品
        keyword = '手机'
        logger.info(f'搜索关键词: {keyword}')
        products = spider.search_products(keyword, pages=2)
        
        if not products:
            logger.warning('没有找到商品')
            return
        
        # 显示结果统计
        logger.info(f'总共找到: {len(products)} 件商品')
        
        # 显示前几条数据
        logger.info('前3件商品数据:')
        for i, product in enumerate(products[:3], 1):
            logger.info(f'{i}. {product.get("title", "未知")}')
            logger.info(f'   价格: {product.get("price", "未知")}')
            logger.info(f'   店铺: {product.get("shop", "未知")}')
        
        # 保存数据
        storage = get_storage('json')
        storage.save(products, 'products.json')
        
        # 也保存为 CSV 格式
        storage_csv = get_storage('csv')
        storage_csv.save(products, 'products.csv')
        
        logger.info('='*50)
        logger.info('爬虫运行完成！')
        logger.info('='*50)
        
    except Exception as e:
        logger.error(f'爬虫运行出错: {e}', exc_info=True)
    finally:
        # 关闭爬虫
        spider.close()


if __name__ == '__main__':
    main()
