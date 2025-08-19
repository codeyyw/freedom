-- fund_test definition

-- Drop table

-- DROP TABLE public.fund_test;

CREATE TABLE public.fund_test (
	id serial4 NOT NULL,
	fund_code varchar(50) NOT NULL,
	fund_name varchar(200) NOT NULL,
	fund_type varchar(100) NOT NULL,
	latest_price numeric(15, 4) NULL,
	insert_time timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	update_time timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	status public."listing_status" DEFAULT 'L'::listing_status NULL,
	CONSTRAINT pk_public_fund_test PRIMARY KEY (id)
)
WITH (
	fillfactor=80
);

-- Create unique index for fund_code
CREATE UNIQUE INDEX idx_fund_test_code ON public.fund_test (fund_code);

-- Table Triggers
create trigger trg_fund_test_update_time before
update
    on
    public.fund_test for each row execute function set_update_time();

-- Comments
COMMENT ON TABLE public.fund_test IS '基金信息测试表，结构与fund_info表相同';
COMMENT ON COLUMN public.fund_test.id IS '主键ID';
COMMENT ON COLUMN public.fund_test.fund_code IS '基金代码';
COMMENT ON COLUMN public.fund_test.fund_name IS '基金名称';
COMMENT ON COLUMN public.fund_test.fund_type IS '基金类型';
COMMENT ON COLUMN public.fund_test.latest_price IS '最新净值';
COMMENT ON COLUMN public.fund_test.insert_time IS '插入时间';
COMMENT ON COLUMN public.fund_test.update_time IS '更新时间';
COMMENT ON COLUMN public.fund_test.status IS '状态';

-- Sample data for testing (optional)
-- INSERT INTO public.fund_test (fund_code, fund_name, fund_type, latest_price, status) VALUES
-- ('000001', '华夏成长混合', '混合型', 1.2345, 'L'),
-- ('000002', '易方达价值精选混合', '混合型', 2.1234, 'L'),
-- ('000003', '南方积极配置混合', '混合型', 1.8765, 'L');