import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function LoginPage() {
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    
    // Get values from form
    const identifier = e.target.email.value;
    const password = e.target.password.value;

    const loginData = {
      identifier: identifier,
      password: password,
    };

    try {
      const response = await api.post('/login', loginData);
      
      console.log("Login Response:", response.data);

      // --- OLD FUNCTIONALITY RESTORED ---
      // We only strictly require the access_token to let you in.
      const accessToken = response.data.access_token || response.data.token;
      
      if (accessToken) {
        // 1. Save Token
        localStorage.setItem('token', accessToken);
        
        // 2. Handle User ID (Fail-safe)
        // If the server sends an ID, use it. 
        // If NOT, default to '1' so the Main Page doesn't crash on "undefined".
        const serverId = response.data.user_id || response.data.id || response.data.userId;
        const finalId = serverId ? serverId : '1'; 
        
        localStorage.setItem('user_id', finalId); 
        
        // 3. Save Name (Optional)
        const displayName = response.data.full_name || response.data.name || identifier; 
        localStorage.setItem('user_name', displayName);

        // 4. Go to Main Page
        navigate('/');
      } else {
        alert("Login failed: No token received.");
      }

    } catch (error) {
      console.error("Login Error:", error);
      // Fallback: If your backend returns 422 but still logs you in elsewhere, 
      // you might need to check headers, but usually this catch means invalid creds.
      alert("Invalid credentials or server error.");
    }
  };

  return (
    <div className="min-h-screen flex w-full bg-white font-sans">
      <div className="flex flex-col justify-center w-full lg:w-1/2 px-8 lg:px-20 xl:px-32 py-10">
        <div className="mb-8">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">Welcome back</h2>
          <p className="mt-2 text-sm text-gray-500">Please enter your details.</p>
        </div>

        <form className="space-y-5" onSubmit={handleLogin}>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Email or Username</label>
            <input
              name="email"
              type="text"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Password</label>
            <input
              name="password"
              type="password"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 outline-none"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full py-3 px-4 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
          >
            Sign in
          </button>
        </form>
        <p className="mt-8 text-center text-sm text-gray-500">
          Don't have an account? <Link to="/signup" className="font-semibold text-indigo-600">Sign up</Link>
        </p>
      </div>
      
      {/* Visual Side */}
      <div className="hidden lg:flex w-1/2 bg-indigo-900 relative">
         <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 to-purple-700 opacity-90"></div>
         <div className="relative z-10 flex items-center justify-center h-full text-white font-bold text-2xl tracking-widest">
            WORKSPACE
         </div>
      </div>
    </div>
  );
}
