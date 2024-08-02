import time
import json

def print_console_ai_message(response_chunks:str, delay:float=0.05):
    print('AI: ', end='', flush=True)
    for ch in response_chunks.split(" "):
        print(f"{ch} ", end='', flush=True)
        time.sleep(delay)
    print("\n")

def send_stream_ai_message(response_chunks:str, delay:float=0.05):
    for ch in response_chunks.split(" "):
        json_str = json.dumps({"html": f"{ch} "})
        yield f"data: {json_str}\n\n"
        # yield f"data: {json.dumps({'text': f'{chunk} '})}\n\n"
        time.sleep(delay)
        
    yield ""

# def send_stream_fastapi_ai_message(response_chunks, chunk_index=0, delay:float=0.02):
#         if chunk_index < len(response_chunks):
#             chunk = response_chunks[chunk_index]
#             yield f"data: {json.dumps({'text': f'{chunk} '})}\n\n"
#             time.sleep(delay)
#             yield from send_stream_fastapi_ai_message(response_chunks, chunk_index + 1)
#         else:
#             yield ""

def get_fake_message():
    messages = [
        "Với mức giá hiện tại, quy đổi theo tỉ giá niêm yết tại ngân hàng, giá vàng thế giới hiện tương đương 74,87 triệu đồng/lượng."
        "\n\n"
        "Trong khi đó trong nước, giá vàng miếng SJC sáng nay tăng 800.000 đồng/lượng, lên mức 79,8 triệu đồng/lượng."
        "\n\n"
        "So với giá vàng thế giới quy đổi, giá vàng miếng SJC đang cao hơn 4,93 triệu đồng/lượng."
        "\n\n"
        "Còn vàng nhẫn 9999 hôm nay tăng 350.000 đồng/lượng, lên 77,65 triệu đồng/lượng theo đà tăng của giá vàng thế giới. "
        "Nếu tính chung trong hai ngày qua, giá vàng nhẫn 9999 đã tăng tổng cộng 650.000 đồng/lượng."
        "\n\n"
        "Giá mua vào vàng nhẫn cũng tăng lên mức 76,3 triệu đồng/lượng."
    ]

    return "".join(messages).replace("\n", "<br>")
