SELECT DISTINCT cur_move_log.board AS cur_board, cur_move_log.move, move_log.board AS next_board
FROM
	(
		SELECT game_log.*, move_log.*, move_log.turn_num + 2 AS next_turn_num 
		FROM game_log INNER JOIN move_log ON game_log.game_id = move_log.game_id
		WHERE move_log.board = :fen_board AND game_log.plr_X_name = :plr_name AND game_log.plr_X_color_int = :plr_color_int
	) AS cur_move_log INNER JOIN move_log 
		ON cur_move_log.game_id = move_log.game_id
		AND cur_move_log.next_turn_num = move_log.turn_num
ORDER BY
	cur_move_log.move, next_board
;