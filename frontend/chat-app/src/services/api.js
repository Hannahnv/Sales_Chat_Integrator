const API_URL = 'http://localhost:8000/sales/api/';

//Hàm login gửi thông tin đăng nhập đến server, nhận token và lưu trữ nó trong localStorage.

export const login = async (username, password) => {
    const response = await fetch(`${API_URL}token/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access);  
        return data;
    } else {
        const errorText = await response.text();
        console.error('Login failed:', response.status, errorText);
        throw new Error('Login failed' + errorText);
    }
};

//Hàm logout xóa token khỏi localStorage, hiệu quả là đăng xuất người dùng.

export const logout = () => {
    localStorage.removeItem('token');  
};


//Token: Là một chuỗi ký tự được sử dụng để xác thực người dùng và cho phép truy cập vào các tài nguyên bảo mật.
//localStorage: Là một bộ nhớ lưu trữ dữ liệu của trình duyệt, được sử dụng để lưu trữ thông tin cục bộ của ứng dụng.
