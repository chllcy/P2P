CREATE TABLE `smzdm_www_info` (
  `title` varchar(256) DEFAULT NULL COMMENT '标题',
  `price` varchar(128) DEFAULT NULL COMMENT '价格信息',
  `url` varchar(128) DEFAULT NULL,
  `support` varchar(64) DEFAULT NULL COMMENT '推荐人',
  `shortdesc` varchar(128) DEFAULT NULL,
  `longdesc` varchar(512) DEFAULT NULL,
  `zhi` int(11) DEFAULT NULL,
  `buzhi` int(11) DEFAULT NULL,
  `fav` int(11) DEFAULT NULL COMMENT '收藏数',
  `comment_number` int(11) DEFAULT NULL COMMENT '评论数',
  `show_time` varchar(16) DEFAULT NULL COMMENT '页面时间',
  `source` varchar(64) DEFAULT NULL COMMENT '来源',
  `insertdate` datetime DEFAULT NULL,
  `updatedate` datetime DEFAULT NULL,
  `www` varchar(16) DEFAULT NULL,
  UNIQUE KEY `smzdm_www_title_date` (`title`,`insertdate`),
  KEY `smzdm_www_title` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8