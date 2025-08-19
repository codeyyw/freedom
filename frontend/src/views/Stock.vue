<template>
  <div class="stock-page">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">股票市场</h1>
        <p class="page-subtitle">实时股票行情，专业投资分析</p>
      </div>

      <!-- 搜索和筛选 -->
      <div class="search-section">
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索股票代码或名称..."
            class="search-input"
          >
          <button class="btn btn-primary">搜索</button>
        </div>
        <div class="filter-tabs">
          <button 
            v-for="tab in filterTabs" 
            :key="tab.key"
            class="filter-tab"
            :class="{ active: activeFilter === tab.key }"
            @click="activeFilter = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- 股票列表 -->
      <div class="stock-table-container">
        <table class="stock-table">
          <thead>
            <tr>
              <th>股票代码</th>
              <th>股票名称</th>
              <th>当前价格</th>
              <th>涨跌幅</th>
              <th>涨跌额</th>
              <th>成交量</th>
              <th>市值</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stock in filteredStocks" :key="stock.code" class="stock-row">
              <td class="stock-code">{{ stock.code }}</td>
              <td class="stock-name">{{ stock.name }}</td>
              <td class="stock-price" :class="stock.changeType">¥{{ stock.price }}</td>
              <td class="stock-change-percent" :class="stock.changeType">{{ stock.changePercent }}</td>
              <td class="stock-change-amount" :class="stock.changeType">{{ stock.changeAmount }}</td>
              <td class="stock-volume">{{ stock.volume }}</td>
              <td class="stock-market-cap">{{ stock.marketCap }}</td>
              <td class="stock-actions">
                <button class="btn btn-sm" @click="viewDetail(stock)">详情</button>
                <button class="btn btn-primary btn-sm" @click="addToWatchlist(stock)">关注</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button class="btn" :disabled="currentPage === 1" @click="currentPage--">上一页</button>
        <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        <button class="btn" :disabled="currentPage === totalPages" @click="currentPage++">下一页</button>
      </div>
    </div>

    <!-- 股票详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedStock.name }} ({{ selectedStock.code }})</h3>
          <button class="modal-close" @click="closeDetailModal">×</button>
        </div>
        <div class="modal-body">
          <div class="stock-detail-info">
            <div class="detail-item">
              <label>当前价格:</label>
              <span class="price" :class="selectedStock.changeType">¥{{ selectedStock.price }}</span>
            </div>
            <div class="detail-item">
              <label>涨跌幅:</label>
              <span :class="selectedStock.changeType">{{ selectedStock.changePercent }}</span>
            </div>
            <div class="detail-item">
              <label>今日开盘:</label>
              <span>¥{{ selectedStock.openPrice }}</span>
            </div>
            <div class="detail-item">
              <label>今日最高:</label>
              <span>¥{{ selectedStock.highPrice }}</span>
            </div>
            <div class="detail-item">
              <label>今日最低:</label>
              <span>¥{{ selectedStock.lowPrice }}</span>
            </div>
            <div class="detail-item">
              <label>成交量:</label>
              <span>{{ selectedStock.volume }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Stock',
  data() {
    return {
      searchQuery: '',
      activeFilter: 'all',
      currentPage: 1,
      pageSize: 20,
      showDetailModal: false,
      selectedStock: {},
      filterTabs: [
        { key: 'all', label: '全部' },
        { key: 'up', label: '上涨' },
        { key: 'down', label: '下跌' },
        { key: 'hot', label: '热门' }
      ],
      stocks: [
        {
          code: '000001',
          name: '平安银行',
          price: '12.45',
          changePercent: '+1.23%',
          changeAmount: '+0.15',
          changeType: 'up',
          volume: '1.2亿',
          marketCap: '2,410亿',
          openPrice: '12.30',
          highPrice: '12.50',
          lowPrice: '12.20'
        },
        {
          code: '000002',
          name: '万科A',
          price: '18.67',
          changePercent: '-0.56%',
          changeAmount: '-0.11',
          changeType: 'down',
          volume: '8,500万',
          marketCap: '2,056亿',
          openPrice: '18.80',
          highPrice: '18.85',
          lowPrice: '18.60'
        },
        {
          code: '000858',
          name: '五粮液',
          price: '156.78',
          changePercent: '+2.34%',
          changeAmount: '+3.58',
          changeType: 'up',
          volume: '4,200万',
          marketCap: '6,089亿',
          openPrice: '153.20',
          highPrice: '157.00',
          lowPrice: '152.80'
        },
        {
          code: '600036',
          name: '招商银行',
          price: '45.23',
          changePercent: '+0.89%',
          changeAmount: '+0.40',
          changeType: 'up',
          volume: '6,800万',
          marketCap: '1.2万亿',
          openPrice: '44.83',
          highPrice: '45.50',
          lowPrice: '44.70'
        },
        {
          code: '600519',
          name: '贵州茅台',
          price: '1678.90',
          changePercent: '-1.23%',
          changeAmount: '-20.90',
          changeType: 'down',
          volume: '180万',
          marketCap: '2.1万亿',
          openPrice: '1699.80',
          highPrice: '1705.00',
          lowPrice: '1675.00'
        },
        {
          code: '000858',
          name: '腾讯控股',
          price: '356.78',
          changePercent: '+1.45%',
          changeAmount: '+5.10',
          changeType: 'up',
          volume: '2,100万',
          marketCap: '3.4万亿',
          openPrice: '351.68',
          highPrice: '358.00',
          lowPrice: '350.50'
        }
      ]
    }
  },
  computed: {
    filteredStocks() {
      let filtered = this.stocks
      
      // 按筛选条件过滤
      if (this.activeFilter === 'up') {
        filtered = filtered.filter(stock => stock.changeType === 'up')
      } else if (this.activeFilter === 'down') {
        filtered = filtered.filter(stock => stock.changeType === 'down')
      }
      
      // 按搜索关键词过滤
      if (this.searchQuery) {
        filtered = filtered.filter(stock => 
          stock.name.includes(this.searchQuery) || 
          stock.code.includes(this.searchQuery)
        )
      }
      
      return filtered
    },
    totalPages() {
      return Math.ceil(this.filteredStocks.length / this.pageSize)
    }
  },
  methods: {
    viewDetail(stock) {
      this.selectedStock = stock
      this.showDetailModal = true
    },
    closeDetailModal() {
      this.showDetailModal = false
      this.selectedStock = {}
    },
    addToWatchlist(stock) {
      alert(`已将 ${stock.name} 添加到关注列表`)
    }
  }
}
</script>

<style scoped lang="scss">
.stock-page {
  padding: $spacing-xl 0;
  min-height: calc(100vh - 64px);
}

.page-header {
  text-align: center;
  margin-bottom: $spacing-xl;
  
  .page-title {
    font-size: 32px;
    font-weight: bold;
    margin-bottom: $spacing-sm;
  }
  
  .page-subtitle {
    color: $text-color-secondary;
    font-size: $font-size-lg;
  }
}

.search-section {
  margin-bottom: $spacing-xl;
  
  .search-bar {
    display: flex;
    gap: $spacing-md;
    margin-bottom: $spacing-lg;
    
    .search-input {
      flex: 1;
      padding: $spacing-sm $spacing-md;
      border: 1px solid $border-color;
      border-radius: $border-radius-base;
      font-size: $font-size-base;
      
      &:focus {
        outline: none;
        border-color: $primary-color;
      }
    }
  }
  
  .filter-tabs {
    display: flex;
    gap: $spacing-sm;
    
    .filter-tab {
      padding: $spacing-sm $spacing-md;
      border: 1px solid $border-color;
      background: white;
      border-radius: $border-radius-base;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        border-color: $primary-color;
        color: $primary-color;
      }
      
      &.active {
        background: $primary-color;
        border-color: $primary-color;
        color: white;
      }
    }
  }
}

.stock-table-container {
  background: white;
  border-radius: $border-radius-lg;
  box-shadow: $box-shadow-card;
  overflow: hidden;
  margin-bottom: $spacing-xl;
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: $spacing-md;
    text-align: left;
    border-bottom: 1px solid #f0f0f0;
  }
  
  th {
    background: #fafafa;
    font-weight: bold;
    color: $text-color;
  }
  
  .stock-row {
    transition: background-color 0.3s;
    
    &:hover {
      background: #f9f9f9;
    }
  }
  
  .stock-code {
    font-family: monospace;
    color: $text-color-secondary;
  }
  
  .stock-name {
    font-weight: bold;
  }
  
  .stock-price, .stock-change-percent, .stock-change-amount {
    font-weight: bold;
    
    &.up { color: $stock-up-color; }
    &.down { color: $stock-down-color; }
  }
  
  .stock-actions {
    .btn {
      margin-right: $spacing-xs;
      
      &.btn-sm {
        padding: 4px 8px;
        font-size: $font-size-sm;
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: $spacing-md;
  
  .page-info {
    color: $text-color-secondary;
  }
}

// 弹窗样式
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: $border-radius-lg;
  box-shadow: $box-shadow-card;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  border-bottom: 1px solid #f0f0f0;
  
  h3 {
    margin: 0;
    font-size: $font-size-xl;
  }
  
  .modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: $text-color-secondary;
    
    &:hover {
      color: $text-color;
    }
  }
}

.modal-body {
  padding: $spacing-lg;
}

.stock-detail-info {
  .detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-sm 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    label {
      font-weight: bold;
      color: $text-color-secondary;
    }
    
    span {
      &.up { color: $stock-up-color; }
      &.down { color: $stock-down-color; }
    }
  }
}

@media (max-width: $breakpoint-md) {
  .search-bar {
    flex-direction: column;
  }
  
  .filter-tabs {
    flex-wrap: wrap;
  }
  
  .stock-table {
    font-size: $font-size-sm;
    
    th, td {
      padding: $spacing-sm;
    }
  }
  
  .stock-actions {
    .btn {
      display: block;
      margin-bottom: $spacing-xs;
      width: 100%;
    }
  }
}
</style>