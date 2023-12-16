-- Does expression * NULL return NULL?
-- How about with other arithmetic operators?
-- If so, we can simplify the aggregation to eliminate CASE and/or nested CASE statements
SELECT 
	move_log.move, 
	count(move_log.move) AS move_count,
	count(CASE 
		WHEN game_log.victor_name = :plr_name AND game_log.victor_color_int = :plr_color_int
		THEN move_log.move ELSE NULL END) AS win_count,
	count(CASE
		WHEN game_log.vic_chk = 0
		THEN move_log.move ELSE NULL END) AS draw_count,
	count(CASE
		WHEN game_log.vic_chk = 1 AND (game_log.victor_name <> :plr_name OR game_log.victor_color_int <> :plr_color_int)
		THEN move_log.move ELSE NULL END) AS loss_count,
	sum(CASE
		WHEN game_log.victor_name = :plr_name AND game_log.victor_color_int = :plr_color_int
		THEN (1.0 / 1.0)
		ELSE NULL END) AS sum_win_factor,
	sum(CASE
		WHEN game_log.vic_chk = 0
		THEN (0.0 / 1.0)
		ELSE NULL END) AS sum_draw_factor,
	sum(CASE
		WHEN game_log.vic_chk = 1 AND (game_log.victor_name <> :plr_name OR game_log.victor_color_int <> :plr_color_int)
		THEN (-1.0 / 1.0)
		ELSE NULL END) AS sum_loss_factor,
	avg(CASE
		WHEN game_log.victor_name = :plr_name AND game_log.victor_color_int = :plr_color_int
		THEN (1.0 / 1.0)
		ELSE NULL END) AS avg_win_factor,
	avg(CASE
		WHEN game_log.vic_chk = 0
		THEN (0.0 / 1.0)
		ELSE NULL END) AS avg_draw_factor,
	avg(CASE
		WHEN game_log.vic_chk = 1 AND (game_log.victor_name <> :plr_name OR game_log.victor_color_int <> :plr_color_int)
		THEN (-1.0 / 1.0)
		ELSE NULL END) AS avg_loss_factor,
	sum(CASE 
		WHEN game_log.victor_name = :plr_name AND game_log.victor_color_int = :plr_color_int
		THEN (1.0 / 1.0)
		WHEN game_log.vic_chk = 0
		THEN (0.0 / 1.0)
		WHEN game_log.vic_chk = 1 AND (game_log.victor_name <> :plr_name OR game_log.victor_color_int <> :plr_color_int)
		THEN (-1.0 / 1.0)
		ELSE NULL END) AS sum_net_factor,
	avg(CASE 
		WHEN game_log.victor_name = :plr_name AND game_log.victor_color_int = :plr_color_int
		THEN (1.0 / 1.0)
		WHEN game_log.vic_chk = 0
		THEN (0.0 / 1.0)
		WHEN game_log.vic_chk = 1 AND (game_log.victor_name <> :plr_name OR game_log.victor_color_int <> :plr_color_int)
		THEN (-1.0 / 1.0)
		ELSE NULL END) AS avg_net_factor
FROM
	game_log INNER JOIN move_log
		ON game_log.game_id = move_log.game_id
WHERE
	move_log.board = :fen_board
	AND game_log.plr_X_name = :plr_name
	AND game_log.plr_X_color_int = :plr_color_int
GROUP BY
	move_log.move
ORDER BY
	(win_count - loss_count) DESC,
	move_log.move
;