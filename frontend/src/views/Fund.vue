<template>
  <div class="fund-page">
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">基金市场</h1>
        <p class="page-subtitle">专业基金投资，稳健财富增长</p>
      </div>

      <!-- 搜索和筛选 -->
      <div class="search-section">
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索基金代码或名称..."
            class="search-input"
          >
          <button class="btn btn-primary">搜索</button>
        </div>
        <div class="filter-section">
          <div class="filter-group">
            <label>基金类型:</label>
            <select v-model="selectedType" class="filter-select">
              <option value="">全部类型</option>
              <option value="股票型">股票型</option>
              <option value="混合型">混合型</option>
              <option value="债券型">债券型</option>
              <option value="指数型">指数型</option>
              <option value="货币型">货币型</option>
            </select>
          </div>
          <div class="filter-group">
            <label>收益排序:</label>
            <select v-model="sortBy" class="filter-select">
              <option value="">默认排序</option>
              <option value="return_desc">收益率从高到低</option>
              <option value="return_asc">收益率从低到高</option>
              <option value="nav_desc">净值从高到低</option>
              <option value="nav_asc">净值从低到高</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 基金列表 -->
      <div class="fund-grid">
        <div 
          v-for="fund in filteredFunds" 
          :key="fund.code" 
          class="fund-card"
          @click="viewDetail(fund)"
        >
          <div class="fund-header">
            <div class="fund-info">
              <h3 class="fund-name">{{ fund.name }}</h3>
              <div class="fund-code">{{ fund.code }}</div>
            </div>
            <div class="fund-type-badge" :class="fund.type.replace('型', '')">
              {{ fund.type }}
            </div>
          </div>
          
          <div class="fund-performance">
            <div class="nav-section">
              <div class="nav-label">单位净值</div>
              <div class="nav-value">¥{{ fund.nav }}</div>
              <div class="nav-date">{{ fund.navDate }}</div>
            </div>
            
            <div class="return-section">
              <div class="return-item">
                <span class="return-label">日涨跌:</span>
                <span class="return-value" :class="fund.dailyReturnType">{{ fund.dailyReturn }}</span>
              </div>
              <div class="return-item">
                <span class="return-label">近一月:</span>
                <span class="return-value" :class="fund.monthReturnType">{{ fund.monthReturn }}</span>
              </div>
              <div class="return-item">
                <span class="return-label">近一年:</span>
                <span class="return-value" :class="fund.yearReturnType">{{ fund.yearReturn }}</span>
              </div>
            </div>
          </div>
          
          <div class="fund-manager">
            <div class="manager-info">
              <span class="manager-label">基金经理:</span>
              <span class="manager-name">{{ fund.manager }}</span>
            </div>
            <div class="fund-scale">规模: {{ fund.scale }}</div>
          </div>
          
          <div class="fund-actions">
            <button class="btn btn-sm" @click.stop="addToWatchlist(fund)">关注</button>
            <button class="btn btn-primary btn-sm" @click.stop="buyFund(fund)">购买</button>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button class="btn" :disabled="currentPage === 1" @click="currentPage--">上一页</button>
        <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        <button class="btn" :disabled="currentPage === totalPages" @click="currentPage++">下一页</button>
      </div>
    </div>

    <!-- 基金详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedFund.name }}</h3>
          <button class="modal-close" @click="closeDetailModal">×</button>
        </div>
        <div class="modal-body">
          <div class="fund-detail-tabs">
            <button 
              v-for="tab in detailTabs" 
              :key="tab.key"
              class="detail-tab"
              :class="{ active: activeDetailTab === tab.key }"
              @click="activeDetailTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
          
          <div class="detail-content">
            <div v-if="activeDetailTab === 'basic'" class="basic-info">
              <div class="detail-item">
                <label>基金代码:</label>
                <span>{{ selectedFund.code }}</span>
              </div>
              <div class="detail-item">
                <label>基金类型:</label>
                <span>{{ selectedFund.type }}</span>
              </div>
              <div class="detail-item">
                <label>单位净值:</label>
                <span>¥{{ selectedFund.nav }}</span>
              </div>
              <div class="detail-item">
                <label>基金经理:</label>
                <span>{{ selectedFund.manager }}</span>
              </div>
              <div class="detail-item">
                <label>基金规模:</label>
                <span>{{ selectedFund.scale }}</span>
              </div>
              <div class="detail-item">
                <label>成立日期:</label>
                <span>{{ selectedFund.establishDate }}</span>
              </div>
            </div>
            
            <div v-if="activeDetailTab === 'performance'" class="performance-info">
              <div class="performance-chart">
                <h4>收益率走势</h4>
                <div class="chart-placeholder">
                  📈 收益率图表（此处可集成图表库）
                </div>
              </div>
              <div class="performance-stats">
                <div class="stat-item">
                  <label>日涨跌:</label>
                  <span :class="selectedFund.dailyReturnType">{{ selectedFund.dailyReturn }}</span>
                </div>
                <div class="stat-item">
                  <label>近一周:</label>
                  <span :class="selectedFund.weekReturnType">{{ selectedFund.weekReturn }}</span>
                </div>
                <div class="stat-item">
                  <label>近一月:</label>
                  <span :class="selectedFund.monthReturnType">{{ selectedFund.monthReturn }}</span>
                </div>
                <div class="stat-item">
                  <label>近三月:</label>
                  <span :class="selectedFund.quarterReturnType">{{ selectedFund.quarterReturn }}</span>
                </div>
                <div class="stat-item">
                  <label>近一年:</label>
                  <span :class="selectedFund.yearReturnType">{{ selectedFund.yearReturn }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Fund',
  data() {
    return {
      searchQuery: '',
      selectedType: '',
      sortBy: '',
      currentPage: 1,
      pageSize: 12,
      showDetailModal: false,
      selectedFund: {},
      activeDetailTab: 'basic',
      detailTabs: [
        { key: 'basic', label: '基本信息' },
        { key: 'performance', label: '业绩表现' }
      ],
      funds: [
        {
          code: '110022',
          name: '易方达消费行业股票',
          type: '股票型',
          nav: '3.456',
          navDate: '2024-01-15',
          dailyReturn: '+1.23%',
          dailyReturnType: 'up',
          weekReturn: '+2.45%',
          weekReturnType: 'up',
          monthReturn: '+5.67%',
          monthReturnType: 'up',
          quarterReturn: '+12.34%',
          quarterReturnType: 'up',
          yearReturn: '+15.67%',
          yearReturnType: 'up',
          manager: '萧楠',
          scale: '156.78亿',
          establishDate: '2010-08-20'
        },
        {
          code: '161725',
          name: '招商中证白酒指数',
          type: '指数型',
          nav: '1.234',
          navDate: '2024-01-15',
          dailyReturn: '-0.56%',
          dailyReturnType: 'down',
          weekReturn: '+1.23%',
          weekReturnType: 'up',
          monthReturn: '+3.45%',
          monthReturnType: 'up',
          quarterReturn: '+6.78%',
          quarterReturnType: 'up',
          yearReturn: '+8.90%',
          yearReturnType: 'up',
          manager: '侯昊',
          scale: '89.45亿',
          establishDate: '2015-05-27'
        },
        {
          code: '000001',
          name: '华夏成长混合',
          type: '混合型',
          nav: '2.789',
          navDate: '2024-01-15',
          dailyReturn: '+0.89%',
          dailyReturnType: 'up',
          weekReturn: '-1.23%',
          weekReturnType: 'down',
          monthReturn: '+2.34%',
          monthReturnType: 'up',
          quarterReturn: '+4.56%',
          quarterReturnType: 'up',
          yearReturn: '-2.34%',
          yearReturnType: 'down',
          manager: '张弘弢',
          scale: '234.56亿',
          establishDate: '2001-12-18'
        },
        {
          code: '519674',
          name: '银河创新成长混合',
          type: '混合型',
          nav: '4.567',
          navDate: '2024-01-15',
          dailyReturn: '+2.10%',
          dailyReturnType: 'up',
          weekReturn: '+3.45%',
          weekReturnType: 'up',
          monthReturn: '+7.89%',
          monthReturnType: 'up',
          quarterReturn: '+15.67%',
          quarterReturnType: 'up',
          yearReturn: '+12.45%',
          yearReturnType: 'up',
          manager: '郑巍山',
          scale: '67.89亿',
          establishDate: '2004-04-30'
        },
        {
          code: '110003',
          name: '易方达上证50指数',
          type: '指数型',
          nav: '1.890',
          navDate: '2024-01-15',
          dailyReturn: '+0.45%',
          dailyReturnType: 'up',
          weekReturn: '+1.67%',
          weekReturnType: 'up',
          monthReturn: '+3.21%',
          monthReturnType: 'up',
          quarterReturn: '+5.43%',
          quarterReturnType: 'up',
          yearReturn: '+7.65%',
          yearReturnType: 'up',
          manager: '余海燕',
          scale: '123.45亿',
          establishDate: '2004-03-22'
        },
        {
          code: '000478',
          name: '建信中证红利潜力指数',
          type: '指数型',
          nav: '2.345',
          navDate: '2024-01-15',
          dailyReturn: '-0.23%',
          dailyReturnType: 'down',
          weekReturn: '+0.89%',
          weekReturnType: 'up',
          monthReturn: '+2.10%',
          monthReturnType: 'up',
          quarterReturn: '+4.32%',
          quarterReturnType: 'up',
          yearReturn: '+6.54%',
          yearReturnType: 'up',
          manager: '梁洪昀',
          scale: '45.67亿',
          establishDate: '2014-01-27'
        }
      ]
    }
  },
  computed: {
    filteredFunds() {
      let filtered = this.funds
      
      // 按类型过滤
      if (this.selectedType) {
        filtered = filtered.filter(fund => fund.type === this.selectedType)
      }
      
      // 按搜索关键词过滤
      if (this.searchQuery) {
        filtered = filtered.filter(fund => 
          fund.name.includes(this.searchQuery) || 
          fund.code.includes(this.searchQuery)
        )
      }
      
      // 排序
      if (this.sortBy) {
        filtered = [...filtered].sort((a, b) => {
          switch (this.sortBy) {
            case 'return_desc':
              return parseFloat(b.yearReturn) - parseFloat(a.yearReturn)
            case 'return_asc':
              return parseFloat(a.yearReturn) - parseFloat(b.yearReturn)
            case 'nav_desc':
              return parseFloat(b.nav) - parseFloat(a.nav)
            case 'nav_asc':
              return parseFloat(a.nav) - parseFloat(b.nav)
            default:
              return 0
          }
        })
      }
      
      return filtered
    },
    totalPages() {
      return Math.ceil(this.filteredFunds.length / this.pageSize)
    }
  },
  methods: {
    viewDetail(fund) {
      this.selectedFund = fund
      this.showDetailModal = true
      this.activeDetailTab = 'basic'
    },
    closeDetailModal() {
      this.showDetailModal = false
      this.selectedFund = {}
    },
    addToWatchlist(fund) {
      alert(`已将 ${fund.name} 添加到关注列表`)
    },
    buyFund(fund) {
      alert(`准备购买 ${fund.name}`)
    }
  }
}
</script>

<style scoped lang="scss">
.fund-page {
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
  
  .filter-section {
    display: flex;
    gap: $spacing-lg;
    
    .filter-group {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      
      label {
        font-weight: bold;
        color: $text-color;
      }
      
      .filter-select {
        padding: $spacing-xs $spacing-sm;
        border: 1px solid $border-color;
        border-radius: $border-radius-base;
        background: white;
        
        &:focus {
          outline: none;
          border-color: $primary-color;
        }
      }
    }
  }
}

.fund-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.fund-card {
  background: white;
  border-radius: $border-radius-lg;
  box-shadow: $box-shadow-card;
  padding: $spacing-lg;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
  
  .fund-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: $spacing-md;
    
    .fund-info {
      flex: 1;
      
      .fund-name {
        font-size: $font-size-lg;
        font-weight: bold;
        margin-bottom: $spacing-xs;
        line-height: 1.3;
      }
      
      .fund-code {
        color: $text-color-secondary;
        font-size: $font-size-sm;
        font-family: monospace;
      }
    }
    
    .fund-type-badge {
      padding: 4px 8px;
      border-radius: 12px;
      font-size: $font-size-sm;
      font-weight: bold;
      
      &.股票 {
        background: #ffe7e7;
        color: #d32f2f;
      }
      
      &.混合 {
        background: #fff3e0;
        color: #f57c00;
      }
      
      &.债券 {
        background: #e8f5e8;
        color: #388e3c;
      }
      
      &.指数 {
        background: #e3f2fd;
        color: #1976d2;
      }
      
      &.货币 {
        background: #f3e5f5;
        color: #7b1fa2;
      }
    }
  }
  
  .fund-performance {
    margin-bottom: $spacing-md;
    
    .nav-section {
      text-align: center;
      padding: $spacing-md;
      background: #f9f9f9;
      border-radius: $border-radius-base;
      margin-bottom: $spacing-md;
      
      .nav-label {
        color: $text-color-secondary;
        font-size: $font-size-sm;
        margin-bottom: $spacing-xs;
      }
      
      .nav-value {
        font-size: 24px;
        font-weight: bold;
        color: $primary-color;
        margin-bottom: $spacing-xs;
      }
      
      .nav-date {
        color: $text-color-secondary;
        font-size: $font-size-sm;
      }
    }
    
    .return-section {
      .return-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: $spacing-xs;
        
        .return-label {
          color: $text-color-secondary;
          font-size: $font-size-sm;
        }
        
        .return-value {
          font-weight: bold;
          
          &.up { color: $stock-up-color; }
          &.down { color: $stock-down-color; }
        }
      }
    }
  }
  
  .fund-manager {
    margin-bottom: $spacing-md;
    
    .manager-info {
      margin-bottom: $spacing-xs;
      
      .manager-label {
        color: $text-color-secondary;
        font-size: $font-size-sm;
      }
      
      .manager-name {
        font-weight: bold;
      }
    }
    
    .fund-scale {
      color: $text-color-secondary;
      font-size: $font-size-sm;
    }
  }
  
  .fund-actions {
    display: flex;
    gap: $spacing-sm;
    
    .btn {
      flex: 1;
      
      &.btn-sm {
        padding: $spacing-xs $spacing-sm;
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
  max-width: 600px;
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

.fund-detail-tabs {
  display: flex;
  margin-bottom: $spacing-lg;
  border-bottom: 1px solid #f0f0f0;
  
  .detail-tab {
    padding: $spacing-sm $spacing-md;
    background: none;
    border: none;
    cursor: pointer;
    color: $text-color-secondary;
    border-bottom: 2px solid transparent;
    transition: all 0.3s;
    
    &:hover {
      color: $primary-color;
    }
    
    &.active {
      color: $primary-color;
      border-bottom-color: $primary-color;
    }
  }
}

.detail-content {
  .basic-info, .performance-info {
    .detail-item, .stat-item {
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
  
  .performance-chart {
    margin-bottom: $spacing-lg;
    
    h4 {
      margin-bottom: $spacing-md;
    }
    
    .chart-placeholder {
      height: 200px;
      background: #f9f9f9;
      border-radius: $border-radius-base;
      display: flex;
      align-items: center;
      justify-content: center;
      color: $text-color-secondary;
      font-size: $font-size-lg;
    }
  }
}

@media (max-width: $breakpoint-md) {
  .fund-grid {
    grid-template-columns: 1fr;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .filter-section {
    flex-direction: column;
    gap: $spacing-md;
  }
  
  .fund-header {
    flex-direction: column;
    align-items: flex-start;
    
    .fund-type-badge {
      margin-top: $spacing-sm;
    }
  }
}
</style>