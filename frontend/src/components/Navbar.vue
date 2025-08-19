<template>
  <nav class="navbar">
    <div class="container">
      <div class="navbar-brand">
        <router-link to="/" class="brand-link">
          <span class="brand-icon">📈</span>
          <span class="brand-text">财富门户</span>
        </router-link>
      </div>
      
      <div class="navbar-menu">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
          首页
        </router-link>
        <router-link to="/stocks" class="nav-link" :class="{ active: $route.path === '/stocks' }">
          股票
        </router-link>
        <router-link to="/funds" class="nav-link" :class="{ active: $route.path === '/funds' }">
          基金
        </router-link>
      </div>
      
      <div class="navbar-actions">
        <button class="btn btn-primary">登录</button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navbar'
}
</script>

<style scoped lang="scss">
.navbar {
  background: white;
  box-shadow: $box-shadow-base;
  position: sticky;
  top: 0;
  z-index: 1000;
  
  .container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
  }
}

.navbar-brand {
  .brand-link {
    display: flex;
    align-items: center;
    color: $text-color;
    font-size: $font-size-xl;
    font-weight: bold;
    
    &:hover {
      color: $primary-color;
    }
  }
  
  .brand-icon {
    font-size: 24px;
    margin-right: $spacing-sm;
  }
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  
  .nav-link {
    color: $text-color;
    font-size: $font-size-base;
    padding: $spacing-sm $spacing-md;
    border-radius: $border-radius-base;
    transition: all 0.3s;
    
    &:hover {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }
    
    &.active {
      background: $primary-color;
      color: white;
    }
  }
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

@media (max-width: $breakpoint-md) {
  .navbar-menu {
    display: none;
  }
  
  .navbar-actions {
    .btn {
      padding: $spacing-xs $spacing-sm;
      font-size: $font-size-sm;
    }
  }
}
</style>