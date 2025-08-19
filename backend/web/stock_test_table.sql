-- stock_test definition

-- Drop table

-- DROP TABLE public.stock_test;

CREATE TABLE public.stock_test (
	id serial4 NOT NULL,
	symbol varchar(20) NOT NULL,
	cname varchar(255) NULL,
	"name" varchar(255) NULL,
	category varchar(100) NULL,
	category_id int4 NULL,
	market public."market_type" NOT NULL,
	status public."listing_status" DEFAULT 'L'::listing_status NOT NULL,
	price numeric(12, 4) NULL,
	diff numeric(12, 4) NULL,
	chg numeric(8, 5) NULL,
	preclose numeric(12, 4) NULL,
	"open" numeric(12, 4) NULL,
	high numeric(12, 4) NULL,
	low numeric(12, 4) NULL,
	amplitude numeric(8, 4) NULL,
	volume int8 NULL,
	turnover numeric(20, 2) NULL,
	mktcap numeric(20, 2) NULL,
	pe numeric(12, 4) NULL,
	best_bid_price numeric(12, 4) NULL,
	best_ask_price numeric(12, 4) NULL,
	datetime timestamp NULL,
	insert_time timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	update_time timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT stock_test_pkey PRIMARY KEY (id),
	CONSTRAINT stock_test_volume_check CHECK ((volume >= 0)),
	CONSTRAINT unique_test_symbol_market UNIQUE (symbol, market)
);

-- Table Triggers

create trigger trg_test_update_time before
update
    on
    public.stock_test for each row execute function set_update_time();

-- Comments
COMMENT ON TABLE public.stock_test IS '股票信息测试表，结构与stock_info表相同';
COMMENT ON COLUMN public.stock_test.id IS '主键ID';
COMMENT ON COLUMN public.stock_test.symbol IS '股票代码';
COMMENT ON COLUMN public.stock_test.cname IS '中文名称';
COMMENT ON COLUMN public.stock_test.name IS '英文名称';
COMMENT ON COLUMN public.stock_test.category IS '分类';
COMMENT ON COLUMN public.stock_test.category_id IS '分类ID';
COMMENT ON COLUMN public.stock_test.market IS '市场类型';
COMMENT ON COLUMN public.stock_test.status IS '上市状态';
COMMENT ON COLUMN public.stock_test.price IS '当前价格';
COMMENT ON COLUMN public.stock_test.diff IS '价格变动';
COMMENT ON COLUMN public.stock_test.chg IS '涨跌幅';
COMMENT ON COLUMN public.stock_test.preclose IS '昨收价';
COMMENT ON COLUMN public.stock_test.open IS '开盘价';
COMMENT ON COLUMN public.stock_test.high IS '最高价';
COMMENT ON COLUMN public.stock_test.low IS '最低价';
COMMENT ON COLUMN public.stock_test.amplitude IS '振幅';
COMMENT ON COLUMN public.stock_test.volume IS '成交量';
COMMENT ON COLUMN public.stock_test.turnover IS '成交额';
COMMENT ON COLUMN public.stock_test.mktcap IS '市值';
COMMENT ON COLUMN public.stock_test.pe IS '市盈率';
COMMENT ON COLUMN public.stock_test.best_bid_price IS '最佳买价';
COMMENT ON COLUMN public.stock_test.best_ask_price IS '最佳卖价';
COMMENT ON COLUMN public.stock_test.datetime IS '数据时间';
COMMENT ON COLUMN public.stock_test.insert_time IS '插入时间';
COMMENT ON COLUMN public.stock_test.update_time IS '更新时间';