import type { Product, ForumPost, FeatureEntry } from '../types';

export const mockFeatureEntries: FeatureEntry[] = [
  {
    id: 'idle',
    title: '二手闲置',
    subtitle: '教材、数码、生活用品',
    icon: '/assets/images/icon_idle_bag.png',
    theme: 'green',
    route: '/idle'
  },
  {
    id: 'forum',
    title: '校园论坛',
    subtitle: '学习、生活、经验分享',
    icon: '/assets/images/icon_forum_chat.png',
    theme: 'blue',
    route: '/forum'
  }
];

export const mockProducts: Product[] = [
  {
    id: 1,
    title: '高等数学（第七版）教材',
    description: '福大生工大一自用教材，九成新，笔记清晰工整，期末备考利器，附赠平时作业答案解析。',
    price: 15,
    category: '教材',
    image_url: '/assets/images/goods_math_book.png',
    status: 'AVAILABLE',
    location: '福州大学旗山校区生活一区',
    seller: {
      id: 101,
      name: '数学小佬',
      avatar: '/assets/avatars/avatar_math.png'
    },
    time_ago: '2小时前',
    created_at: '2026-10-15 08:30'
  },
  {
    id: 2,
    title: 'AirPods 3 自用出',
    description: '官网正品国行，带无线充电盒，成色极佳，功能全部完好，音质与续航均正常，送保护套。',
    price: 450,
    category: '数码',
    image_url: '/assets/images/goods_airpods.png',
    status: 'AVAILABLE',
    location: '福州大学旗山校区风雨操场',
    seller: {
      id: 102,
      name: '青柠',
      avatar: '/assets/avatars/avatar_lime.png'
    },
    time_ago: '3小时前',
    created_at: '2026-10-15 07:15'
  },
  {
    id: 3,
    title: '护眼台灯 9成新',
    description: '宿舍自用国誉护眼台灯，无频闪，三档色温调节，触控开关，毕业急出支持面交自提。',
    price: 60,
    category: '生活用品',
    image_url: '/assets/images/goods_desk_lamp.png',
    status: 'AVAILABLE',
    location: '福州大学旗山校区宿舍三区',
    seller: {
      id: 103,
      name: '喵同学',
      avatar: '/assets/avatars/avatar_cat.png'
    },
    time_ago: '5小时前',
    created_at: '2026-10-15 05:20'
  },
  {
    id: 4,
    title: 'iPad Air 5 64G 星光色',
    description: '原装箱说全，带Apple Pencil二代磁吸充电笔，无划痕带类纸膜，送磁吸双面夹保护套。',
    price: 2999,
    category: '数码',
    image_url: '/assets/images/goods_airpods.png',
    status: 'AVAILABLE',
    location: '福州大学图书馆一楼大厅',
    seller: {
      id: 104,
      name: '数码学长',
      avatar: '/assets/avatars/avatar_fzu_daily.png'
    },
    time_ago: '昨天',
    created_at: '2026-10-14 18:00'
  },
  {
    id: 5,
    title: '考研英语二历年真题详解',
    description: '黄皮书全新未动笔，附赠核心词汇背诵手册及真题网盘视频网课，超值出。',
    price: 25,
    category: '教材',
    image_url: '/assets/images/goods_math_book.png',
    status: 'AVAILABLE',
    location: '福州大学公共教学楼文科楼',
    seller: {
      id: 105,
      name: '上岸小锦鲤',
      avatar: '/assets/avatars/avatar_taro.png'
    },
    time_ago: '2天前',
    created_at: '2026-10-13 14:00'
  },
  {
    id: 6,
    title: '美的宿舍静音小风扇',
    description: '四档风速，USB插口充电超长续航，夏天宿舍自习必备，轻便好携带。',
    price: 28,
    category: '生活用品',
    image_url: '/assets/images/goods_desk_lamp.png',
    status: 'AVAILABLE',
    location: '福州大学生活二区菜鸟驿站',
    seller: {
      id: 103,
      name: '喵同学',
      avatar: '/assets/avatars/avatar_cat.png'
    },
    time_ago: '3天前',
    created_at: '2026-10-12 11:30'
  }
];

export const mockForumPosts: ForumPost[] = [
  {
    id: 1,
    title: '福大新生入学指南！从报到到选课全攻略',
    summary: '整理了报到流程、宿舍生活、选课建议等新生必看内容，希望能帮到即将到来的学弟学妹们~',
    content: `亲爱的2026级福大学弟学妹们好！作为在旗山校区生活了三年的老学长，整理了一份超全面的新生避坑与生活指南：

1. 报到与注册：
- 提前准备好录取通知书、身份证、团员档案以及1寸/2寸蓝底白底证件照（建议准备8张以上备用）。
- 进校后按照路标引导，先到各学院大本营办理入住手续领取宿舍钥匙与校园卡。

2. 宿舍生活与必备好物：
- 旗山校区宿舍一般为四人间，上床下桌，配有独立卫浴和空调。
- 建议带上：遮光床帘、护眼台灯、插线板（国标插座）、防蚊驱蚊喷雾。

3. 选课与学分建议：
- 大一选课首推通识必修和体育课，选课系统开放前记得提前把备选课程代码加入预选单！

希望大家在福大遇见更好的自己！有疑问欢迎在评论区随时留言探讨~`,
    tag: '新生指南',
    tagType: 'blue',
    image_url: '/assets/images/forum_freshman.png',
    author: {
      name: '福大日常',
      avatar: '/assets/avatars/avatar_fzu_daily.png'
    },
    comment_count: 32,
    created_date: '08-25',
    likes_count: 128
  },
  {
    id: 2,
    title: '图书馆自习座位预约攻略',
    summary: '整理了图书馆各区域的特点、开放时间和座位预约方式，以及一些自习小建议，欢迎补充~',
    content: `福州大学图书馆座位预约全方位实用指南：

1. 预约规则与开放时间：
- 每天早上 6:30 开放当天和次日座位预约，通过“福州大学微生活”或图书馆微信公众号进入。
- 签到时间为预约开始后 30 分钟内，凭校园卡或二维码在闸机签到。

2. 各楼层自习区域特点：
- 二楼大厅：适合轻声研讨和翻阅期刊，采光好。
- 三楼至五楼静音自习区：考研和期末复习宝地，安静舒适，每个座位均配有独立充电插孔与台灯。
- 六楼电子阅览区：配备电脑，查阅文献论文首选。

大家记得爱护自习环境，离座超过半小时请主动点击暂离哦！`,
    tag: '学习经验',
    tagType: 'green',
    image_url: '/assets/images/forum_library.png',
    author: {
      name: '一颗芋圆',
      avatar: '/assets/avatars/avatar_taro.png'
    },
    comment_count: 18,
    created_date: '08-24',
    likes_count: 85
  },
  {
    id: 3,
    title: '期末高等数学复习划重点与提分技巧',
    summary: '高数期末不挂科秘籍，极限、微分、积分核心公式整理，附历年真题常考题型解构。',
    content: '期末考即将来临，针对大一高数（上/下）为大家梳理了最核心的复习框架：第一抓洛必达法则与泰勒展开，第二抓积分技巧，第三重做课后典型习题。',
    tag: '学习经验',
    tagType: 'green',
    image_url: '/assets/images/goods_math_book.png',
    author: {
      name: '数学小佬',
      avatar: '/assets/avatars/avatar_math.png'
    },
    comment_count: 45,
    created_date: '08-20',
    likes_count: 156
  },
  {
    id: 4,
    title: '福大旗山校区美食地图：从一区吃到三区食堂！',
    summary: '亲测福大各大食堂必吃窗口！瓦罐汤、黄焖鸡、生滚牛肉粉、铁板烧大盘点~',
    content: '在福大吃什么？看这一篇就够了！一区二楼的沙县养生瓦罐汤、二区三楼的特色香锅、以及三区的小炒窗口都是性价比天花板！',
    tag: '生活分享',
    tagType: 'orange',
    image_url: '/assets/images/forum_freshman.png',
    author: {
      name: '青柠',
      avatar: '/assets/avatars/avatar_lime.png'
    },
    comment_count: 67,
    created_date: '08-18',
    likes_count: 210
  }
];

export const mockCurrentUser = {
  id: 1,
  username: '福大学子',
  student_id: '102301520',
  avatar: '/assets/avatars/avatar_cat.png',
  bio: '福州大学 计算机与大数据学院 2023级',
  balance: 320.00,
  published_count: 3,
  favorites_count: 12,
  order_count: 5
};
