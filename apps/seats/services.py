from apps.seats.models import Seat


def generate_seats(venue, block, seat_type, row_start, row_end, number_start, number_end):
    """
    座席を一括生成する
    
    Args:
        venue: Venueオブジェクト
        block: ブロック名 (str)
        seat_type: 座席種別 ('S', 'A', 'B')
        row_start: 開始列 (str or int)
        row_end: 終了列 (str or int)
        number_start: 開始番号 (int)
        number_end: 終了番号 (int)
    
    Returns:
        作成した座席のリスト
    """
    seats_to_create = []
    
    # 列の範囲を生成
    # 数字の場合は数値範囲、文字の場合はアルファベット範囲
    if row_start.isdigit() and row_end.isdigit():
        rows = [str(i) for i in range(int(row_start), int(row_end) + 1)]
    else:
        # アルファベット範囲 (A-Z)
        start_ord = ord(row_start.upper())
        end_ord = ord(row_end.upper())
        rows = [chr(i) for i in range(start_ord, end_ord + 1)]
    
    # 座席を生成
    for row in rows:
        for number in range(number_start, number_end + 1):
            seat = Seat(
                venue=venue,
                block=block,
                row=row,
                number=str(number),
                seat_type=seat_type,
                status='available'
            )
            seats_to_create.append(seat)
    
    # 一括作成
    created_seats = Seat.objects.bulk_create(seats_to_create, ignore_conflicts=True)
    
    return created_seats


def get_seat_map(event, ticket_type):
    """
    座席選択UI用のデータを取得
    
    Args:
        event: Eventオブジェクト
        ticket_type: TicketTypeオブジェクト
    
    Returns:
        dict: 座席データ（ブロック・列・番号でグループ化）
    """
    # イベントの会場の座席を取得
    seats = Seat.objects.filter(
        venue=event.venue
    ).select_related('venue').order_by('block', 'row', 'number')
    
    # 座席データをグループ化
    seat_map = {}
    for seat in seats:
        block = seat.block
        if block not in seat_map:
            seat_map[block] = {}
        
        row = seat.row
        if row not in seat_map[block]:
            seat_map[block][row] = []
        
        seat_map[block][row].append({
            'id': seat.id,
            'number': seat.number,
            'seat_type': seat.seat_type,
            'status': seat.status,
            'price': ticket_type.price,
        })
    
    return seat_map


def get_available_seats_json(event, ticket_type):
    """
    Ajax用の座席データをJSON形式で返す
    
    Args:
        event: Eventオブジェクト
        ticket_type: TicketTypeオブジェクト
    
    Returns:
        list: 座席データのリスト
    """
    seats = Seat.objects.filter(
        venue=event.venue,
        status='available'
    ).order_by('block', 'row', 'number')
    
    seats_data = []
    for seat in seats:
        seats_data.append({
            'id': seat.id,
            'block': seat.block,
            'row': seat.row,
            'number': seat.number,
            'seat_type': seat.seat_type,
            'seat_type_display': seat.get_seat_type_display(),
            'status': seat.status,
            'price': float(ticket_type.price),
            'label': f"{seat.block}-{seat.row}-{seat.number}",
        })
    
    return seats_data
