<template>
  <div class="home">
    <!-- 英雄区域 -->
    <section class="hero">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">智能投资，财富增长</h1>
          <p class="hero-subtitle">实时股票基金数据，专业投资分析，助您把握市场机遇</p>
          <div class="hero-actions">
            <button class="btn btn-primary">开始投资</button>
            <button class="btn">了解更多</button>
          </div>
        </div>
      </div>
    </section>

    <!-- 市场概览 -->
    <section class="market-overview">
      <div class="container">
        <h2 class="section-title">市场概览</h2>
        <div class="row">
          <div class="col col-4">
            <div class="market-card">
              <div class="market-icon">📊</div>
              <h3>上证指数</h3>
              <div class="market-price up">3,245.67</div>
              <div class="market-change up">+1.23%</div>
            </div>
          </div>
          <div class="col col-4">
            <div class="market-card">
              <div class="market-icon">📈</div>
              <h3>深证成指</h3>
              <div class="market-price down">10,876.54</div>
              <div class="market-change down">-0.45%</div>
            </div>
          </div>
          <div class="col col-4">
            <div class="market-card">
              <div class="market-icon">🌟</div>
              <h3>创业板指</h3>
              <div class="market-price up">2,156.89</div>
              <div class="market-change up">+2.10%</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 热门股票 -->
    <section class="hot-stocks">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">热门股票</h2>
          <router-link to="/stocks" class="section-link">查看更多 →</router-link>
        </div>
        <div class="stock-list">
          <div class="stock-item" v-for="stock in hotStocks" :key="stock.code">
            <div class="stock-info">
              <div class="stock-name">{{ stock.name }}</div>
              <div class="stock-code">{{ stock.code }}</div>
            </div>
            <div class="stock-price">
              <div class="price" :class="stock.changeType">¥{{ stock.price }}</div>
              <div class="change" :class="stock.changeType">{{ stock.change }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 推荐基金 -->
    <section class="recommended-funds">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">推荐基金</h2>
          <router-link to="/funds" class="section-link">查看更多 →</router-link>
        </div>
        <div class="row">
          <div class="col col-3" v-for="fund in recommendedFunds" :key="fund.code">
            <div class="fund-card">
              <div class="fund-header">
                <h3 class="fund-name">{{ fund.name }}</h3>
                <div class="fund-type">{{ fund.type }}</div>
              </div>
              <div class="fund-performance">
                <div class="fund-nav">净值: ¥{{ fund.nav }}</div>
                <div class="fund-return" :class="fund.returnType">{{ fund.return }}</div>
              </div>
              <div class="fund-manager">基金经理: {{ fund.manager }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      hotStocks: [
        { code: '000001', name: '平安银行', price: '12.45', change: '+1.23%', changeType: 'up' },
        { code: '000002', name: '万科A', price: '18.67', change: '-0.56%', changeType: 'down' },
        { code: '000858', name: '五粮液', price: '156.78', change: '+2.34%', changeType: 'up' },
        { code: '600036', name: '招商银行', price: '45.23', change: '+0.89%', changeType: 'up' },
        { code: '600519', name: '贵州茅台', price: '1678.90', change: '-1.23%', changeType: 'down' }
      ],
      recommendedFunds: [
        { code: '110022', name: '易方达消费行业', type: '股票型', nav: '3.456', return: '+15.67%', returnType: 'up', manager: '萧楠' },
        { code: '161725', name: '招商中证白酒', type: '指数型', nav: '1.234', return: '+8.90%', returnType: 'up', manager: '侯昊' },
        { code: '000001', name: '华夏成长混合', type: '混合型', nav: '2.789', return: '-2.34%', returnType: 'down', manager: '张弘弢' },
        { code: '519674', name: '银河创新成长', type: '混合型', nav: '4.567', return: '+12.45%', returnType: 'up', manager: '郑巍山' }
      ]
    }
  }
}
</script>

<style scoped lang="scss">
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 0;
  text-align: center;
  
  .hero-title {
    font-size: 48px;
    font-weight: bold;
    margin-bottom: $spacing-md;
  }
  
  .hero-subtitle {
    font-size: $font-size-xl;
    margin-bottom: $spacing-xl;
    opacity: 0.9;
  }
  
  .hero-actions {
    display: flex;
    gap: $spacing-md;
    justify-content: center;
    
    .btn {
      padding: $spacing-md $spacing-xl;
      font-size: $font-size-lg;
      
      &:not(.btn-primary) {
        background: transparent;
        border-color: white;
        color: white;
        
        &:hover {
          background: white;
          color: $primary-color;
        }
      }
    }
  }
}

.market-overview {
  padding: 60px 0;
  background: white;
}

.section-title {
  font-size: $font-size-xxl;
  font-weight: bold;
  margin-bottom: $spacing-xl;
  text-align: center;
}

.market-card {
  background: white;
  border-radius: $border-radius-lg;
  box-shadow: $box-shadow-card;
  padding: $spacing-lg;
  text-align: center;
  transition: transform 0.3s;
  
  &:hover {
    transform: translateY(-4px);
  }
  
  .market-icon {
    font-size: 32px;
    margin-bottom: $spacing-md;
  }
  
  h3 {
    font-size: $font-size-lg;
    margin-bottom: $spacing-sm;
    color: $text-color;
  }
  
  .market-price {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: $spacing-xs;
    
    &.up { color: $stock-up-color; }
    &.down { color: $stock-down-color; }
  }
  
  .market-change {
    font-size: $font-size-base;
    
    &.up { color: $stock-up-color; }
    &.down { color: $stock-down-color; }
  }
}

.hot-stocks, .recommended-funds {
  padding: 60px 0;
  
  &:nth-child(even) {
    background: #fafafa;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-xl;
  
  .section-link {
    color: $primary-color;
    font-size: $font-size-base;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.stock-list {
  display: grid;
  gap: $spacing-md;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: $spacing-md;
  border-radius: $border-radius-base;
  box-shadow: $box-shadow-base;
  transition: transform 0.3s;
  
  &:hover {
    transform: translateX(4px);
  }
  
  .stock-info {
    .stock-name {
      font-weight: bold;
      margin-bottom: $spacing-xs;
    }
    
    .stock-code {
      color: $text-color-secondary;
      font-size: $font-size-sm;
    }
  }
  
  .stock-price {
    text-align: right;
    
    .price {
      font-size: $font-size-lg;
      font-weight: bold;
      margin-bottom: $spacing-xs;
      
      &.up { color: $stock-up-color; }
      &.down { color: $stock-down-color; }
    }
    
    .change {
      font-size: $font-size-sm;
      
      &.up { color: $stock-up-color; }
      &.down { color: $stock-down-color; }
    }
  }
}

.fund-card {
  background: white;
  border-radius: $border-radius-lg;
  box-shadow: $box-shadow-card;
  padding: $spacing-lg;
  transition: transform 0.3s;
  
  &:hover {
    transform: translateY(-4px);
  }
  
  .fund-header {
    margin-bottom: $spacing-md;
    
    .fund-name {
      font-size: $font-size-lg;
      font-weight: bold;
      margin-bottom: $spacing-xs;
    }
    
    .fund-type {
      color: $text-color-secondary;
      font-size: $font-size-sm;
      background: #f0f0f0;
      padding: 2px 8px;
      border-radius: 12px;
      display: inline-block;
    }
  }
  
  .fund-performance {
    margin-bottom: $spacing-md;
    
    .fund-nav {
      margin-bottom: $spacing-xs;
    }
    
    .fund-return {
      font-weight: bold;
      
      &.up { color: $stock-up-color; }
      &.down { color: $stock-down-color; }
    }
  }
  
  .fund-manager {
    color: $text-color-secondary;
    font-size: $font-size-sm;
  }
}

@media (max-width: $breakpoint-md) {
  .hero {
    padding: 40px 0;
    
    .hero-title {
      font-size: 32px;
    }
    
    .hero-actions {
      flex-direction: column;
      align-items: center;
    }
  }
  
  .market-card {
    margin-bottom: $spacing-md;
  }
}
</style>