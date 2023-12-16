SELECT 
	game_log.*, 
	move_log.*
FROM
	game_log INNER JOIN move_log
		ON game_log.game_id = move_log.game_id
WHERE
	move_log.board = :fen_board
	AND game_log.plr_X_name = :plr_name
	AND game_log.plr_X_color_int = :plr_color_int
;