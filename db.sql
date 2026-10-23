-- ==========================================================
-- 学迹 —— 学习打卡与资料共享平台 建表脚本（SQLite）
-- 说明：项目启动时 app/__init__.py 里的 db.create_all() 也会自动建表，
--       这个脚本是给老师看的完整 SQL 版，可用 sqlite3 xueji.sqlite < db.sql 执行。
-- ==========================================================

DROP TABLE IF EXISTS favorite;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS material;
DROP TABLE IF EXISTS checkin;
DROP TABLE IF EXISTS subject;
DROP TABLE IF EXISTS user;

-- 用户表
CREATE TABLE user (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      VARCHAR(32)  NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    email         VARCHAR(120),
    created_at    DATETIME,
    points        INTEGER DEFAULT 0
);
CREATE UNIQUE INDEX ix_user_username ON user (username);

-- 科目表
CREATE TABLE subject (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(32) NOT NULL UNIQUE,
    icon VARCHAR(16) DEFAULT '📘'
);

-- 打卡表（外键指向 user、subject，一对多）
CREATE TABLE checkin (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    duration   INTEGER DEFAULT 0,
    note       TEXT,
    date       DATE,
    created_at DATETIME,
    FOREIGN KEY (user_id)    REFERENCES user (id),
    FOREIGN KEY (subject_id) REFERENCES subject (id)
);
CREATE INDEX ix_checkin_date ON checkin (date);

-- 资料表（外键指向 user）
CREATE TABLE material (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    title       VARCHAR(120) NOT NULL,
    category    VARCHAR(32) DEFAULT '其他',
    description TEXT,
    filename    VARCHAR(200),
    filesize    INTEGER DEFAULT 0,
    downloads   INTEGER DEFAULT 0,
    score_avg   FLOAT DEFAULT 0,
    created_at  DATETIME,
    FOREIGN KEY (user_id) REFERENCES user (id)
);
CREATE INDEX ix_material_category ON material (category);

-- 评论表（外键指向 user、material，一对多）
CREATE TABLE comment (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    rating      INTEGER DEFAULT 5,
    content     TEXT NOT NULL,
    created_at  DATETIME,
    FOREIGN KEY (user_id)     REFERENCES user (id),
    FOREIGN KEY (material_id) REFERENCES material (id)
);

-- 收藏表（user 与 material 的多对多中间表）
CREATE TABLE favorite (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    created_at  DATETIME,
    FOREIGN KEY (user_id)     REFERENCES user (id),
    FOREIGN KEY (material_id) REFERENCES material (id),
    CONSTRAINT uq_user_material UNIQUE (user_id, material_id)
);
