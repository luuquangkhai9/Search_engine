Hệ thống tìm kiếm, truy vấn văn bản 

Thiết lập chạy:
1. Chạy môi trường ảo puython 3.11 (Phiên bản không xảy ra xung đột thư viện)
2. Cài đặt danh sách thư viện có trong requirements.txt
3. Tạo 2 container docker cho postgre và elastic (es phiên bản 8 gặp lỗi bảo mật, dùng phiên bản 7)
    # Thông sô database(postgre):
        DB_NAME = "searchdb_v2"
        DB_USER = "myuser_v2"
        DB_PASS = "mysecretpassword_v2"
        DB_HOST = "localhost"
        DB_PORT = "5433"
    Lệnh tạo :
    elastic
       docker run --name search_es_v2 -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -d docker.elastic.co/elasticsearch/elasticsearch:7.17.14
    database
        docker run --name search_db_v2 -e POSTGRES_PASSWORD=mysecretpassword_v2 -e POSTGRES_USER=myuser_v2 -e POSTGRES_DB=searchdb_v2 -p 5433:5432 -d postgres:15
    


4. chạy file v2_00_migrate_db.py để chuyển dữ liệu lên postgre
        file v2_02_index_es.py thiết lập và lưu index text key vào elastic

5. Chạy lệnh uvicorn api.v2_main:app --reload --port 8000 để hệ thống hoạt động
6. Sử dụng hệ thống qua file index.html
