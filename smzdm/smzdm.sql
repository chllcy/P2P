CREATE TABLE `smzdm_www_info` (
  `title` varchar(256) DEFAULT NULL COMMENT '����',
  `price` varchar(128) DEFAULT NULL COMMENT '�۸���Ϣ',
  `url` varchar(128) DEFAULT NULL,
  `support` varchar(64) DEFAULT NULL COMMENT '�Ƽ���',
  `shortdesc` varchar(128) DEFAULT NULL,
  `longdesc` varchar(512) DEFAULT NULL,
  `zhi` int(11) DEFAULT NULL,
  `buzhi` int(11) DEFAULT NULL,
  `fav` int(11) DEFAULT NULL COMMENT '�ղ���',
  `comment_number` int(11) DEFAULT NULL COMMENT '������',
  `show_time` varchar(16) DEFAULT NULL COMMENT 'ҳ��ʱ��',
  `source` varchar(64) DEFAULT NULL COMMENT '��Դ',
  `insertdate` datetime DEFAULT NULL,
  `updatedate` datetime DEFAULT NULL,
  `www` varchar(16) DEFAULT NULL,
  UNIQUE KEY `smzdm_www_title_date` (`title`,`insertdate`),
  KEY `smzdm_www_title` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8