INSERT INTO move_log (
	game_id,
	board,
	turn,
	move_num,
	turn_num,
	move,
	timestamp
)
VALUES (
	:game_id,
	:board,
	:turn,
	:move_num,
	:turn_num,
	:move,
	:timestamp
)