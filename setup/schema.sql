; Create Database for Snaggy

create database snaggydb;

use snaggydb;

create table article (
  art_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  art_title VARCHAR(25) NOT NULL,
  art_pubdate TIMESTAMP default CURRENT_TIMESTAMP,
  art_added TIMESTAMP default CURRENT_TIMESTAMP,
  art_text MEDIUMTEXT NOT NULL,
  art_url VARCHAR(255) NOT NULL,
  art_imgurl VARCHAR(255),
  PRIMARY KEY (art_id)
);

create table author (
  auth_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  auth_lname VARCHAR(64) NOT NULL,
  auth_fname VARCHAR(64),
  auth_homepage VARCHAR(64),
  valid BOOLEAN NOT NULL default 1,
  PRIMARY KEY (auth_id)
);

create table auth_art_rel (
  auth_art_rel_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  fk_art_id INT UNSIGNED NOT NULL REFERENCES article(art_id),
  fk_auth_id INT UNSIGNED NOT NULL REFERENCES author(auth_id),
  PRIMARY KEY (auth_art_rel_id)
);

create table users (
        uid INT UNSIGNED NOT NULL AUTO_INCREMENT,
        username VARCHAR(64) NOT NULL,
        CONSTRAINT username UNIQUE (username),
        PRIMARY KEY (uid)
);

create table usertokens (
        tokenid INT UNSIGNED NOT NULL AUTO_INCREMENT,
        token VARCHAR(512) NOT NULL,
        tokentype ENUM("PASSWORD", "APITOKEN") NOT NULL,
        fk_uid VARCHAR(64) NOT NULL REFERENCES users(uid),
        token_issue_date TIMESTAMP NOT NULL default CURRENT_TIMESTAMP,
        token_expire_date TIMESTAMP NOT NULL default '0000-00-00 00:00:00' on UPDATE CURRENT_TIMESTAMP,
        salt INT UNSIGNED NOT NULL,
        activated BOOL NOT NULL default true,
        PRIMARY KEY (tokenid)
);

; Sample Command for creating a user Do not run
; without changing password and possibly host
; create user 'snaggy'@'localhost' identified by 'yourdopepassword';
; grant insert, update, select, delete on snaggydb.article to 'snaggy'@'localhost' ;
; grant insert, update, select, delete on snaggydb.author to 'snaggy'@'localhost' ;
; grant insert, update, select, delete on snaggydb.auth_art_rel to 'snaggy'@'localhost' ;
; grant insert, update, select, delete on snaggydb.users to 'snaggy'@'localhost' ;
; grant insert, update, select, delete on snaggydb.usertokens to 'snaggy'@'localhost' ;
