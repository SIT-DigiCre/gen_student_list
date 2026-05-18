# 概要

部員名簿を半自動で作成するやつです

# 準備

ビューの作成(SysDev>知見 内 部員名簿の作成より)
```sql
CREATE VIEW user_full_profiles (
  user_id, active_limit, is_member, is_graduated,
  username, student_number, school_grade, is_male,
  first_name, last_name, phone_number,
  parent_name, parent_first_name, parent_last_name, parent_cellphone_number
) AS (
  SELECT
	  `u`.`id` AS `id`,
    `p`.`active_limit` AS `active_limit`,
    `p`.`is_member` AS `is_member`,
    `p`.`is_graduated` AS `is_graduated`,
    `p`.`username` AS `username`,
    `u`.`student_number` AS `student_number`,
    `p`.`school_grade` AS `school_grade`,
    `pp`.`is_male` AS `is_male`,
    `pp`.`first_name` AS `first_name`,
    `pp`.`last_name` AS `last_name`,
    `pp`.`phone_number` AS `phone_number`,
    `pp`.`parent_name` AS `parent_name`,
    `pp`.`parent_first_name` AS `parent_first_name`,
    `pp`.`parent_last_name` AS `parent_last_name`,
    `pp`.`parent_cellphone_number` AS `parent_cellphone_number`
  FROM `digicre`.`users` `u` 
  LEFT JOIN `digicre`.`user_profiles` `p` ON `u`.`id` = `p`.`user_id`
  LEFT JOIN `digicre`.`user_private_profiles` `pp` ON `u`.`id` = `pp`.`user_id`
);
```
phpMyAdmin上で、
```sql
SELECT student_number, is_male, first_name, last_name, school_grade, phone_number, parent_name, parent_first_name, parent_last_name, parent_cellphone_number FROM `user_full_profiles` WHERE is_member = 1 AND is_graduated = 0 AND active_limit >= TIMESTAMP "<来年度始まり>-05-01 00:00:00";
```
を実行し、`CSV`としてエクスポート

[芝浦工大公式ページ](https://www.shibaura-it.ac.jp/campus_life/guide/document.html)より、部員名簿のフォーマットを落としてくる。  
また、最新の役員変更届(入力済み)もダウンロードしておく。

# 実行

python main.py <デジコアDB CSV> <部員名簿テンプレート xlsx> <役員変更届 docx>
