SELECT 
	:plr_1_name AS plr_1_name,
	:plr_1_text_color AS plr_1_text_color,
	:plr_2_name AS plr_2_name,
	:plr_2_text_color AS plr_2_text_color,
	sum(CASE 
		WHEN plr_X_name = :plr_1_name 
		AND plr_X_color_int = :plr_1_color_int
		AND victor_name = :plr_1_name 
		AND victor_color_int = :plr_1_color_int 
		THEN 1 ELSE 0 END) AS plr_1_X_wins,
	sum(CASE 
		WHEN plr_O_name = :plr_1_name 
		AND plr_O_color_int = :plr_1_color_int
		AND victor_name = :plr_1_name 
		AND victor_color_int = :plr_1_color_int 
		THEN 1 ELSE 0 END) AS plr_1_O_wins,
	sum(CASE 
		WHEN plr_X_name = :plr_2_name 
		AND plr_X_color_int = :plr_2_color_int
		AND victor_name = :plr_2_name 
		AND victor_color_int = :plr_2_color_int 
		THEN 1 ELSE 0 END) AS plr_2_X_wins,
	sum(CASE 
		WHEN plr_O_name = :plr_2_name 
		AND plr_O_color_int = :plr_2_color_int
		AND victor_name = :plr_2_name 
		AND victor_color_int = :plr_2_color_int 
		THEN 1 ELSE 0 END) AS plr_2_O_wins,
	sum(CASE 
		WHEN plr_X_name = :plr_1_name 
		AND plr_X_color_int = :plr_1_color_int
		AND plr_O_name = :plr_2_name 
		AND plr_O_color_int = :plr_2_color_int
		AND victor_name = '' 
		AND victor_color_int = 0
		THEN 1 ELSE 0 END) AS game_X_O_draws,
	sum(CASE 
		WHEN plr_X_name = :plr_2_name 
		AND plr_X_color_int = :plr_2_color_int
		AND plr_O_name = :plr_1_name 
		AND plr_O_color_int = :plr_1_color_int
		AND victor_name = '' 
		AND victor_color_int = 0
		THEN 1 ELSE 0 END) AS game_O_X_draws
FROM game_log
WHERE
	(
		plr_X_name = :plr_1_name 
		AND plr_X_color_int = :plr_1_color_int
		AND plr_O_name = :plr_2_name 
		AND plr_O_color_int = :plr_2_color_int
	) OR (
		plr_X_name = :plr_2_name 
		AND plr_X_color_int = :plr_2_color_int
		AND plr_O_name = :plr_1_name 
		AND plr_O_color_int = :plr_1_color_int
	)
;