import { Link, useNavigate } from 'react-router-dom';
import api from '../api';

export default function SignupPage() {
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();

    // Schema based on your screenshot
    const userData = {
      email: e.target.email.value,
      username: e.target.name.value, // Mapping "Full Name" input to "username"
      password: e.target.password.value,
    };

    try {
      await api.post('/users/', userData);
      alert("Account created! Redirecting to login...");
      navigate('/login');
    } catch (error) {
      console.error("Signup failed:", error.response?.data || error.message);
      alert("Signup failed. Please try again.");
    }
  };

  return (
    // Main Container
    <div className="min-h-screen flex w-full bg-white font-sans">
      
      {/* LEFT COLUMN: Signup Form */}
      <div className="flex flex-col justify-center w-full lg:w-1/2 px-8 lg:px-20 xl:px-32 py-10">
        
        {/* Logo / Header */}
        <div className="mb-8">
          <div className="h-10 w-10 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-xl mb-4 shadow-indigo-200 shadow-lg">
            A
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">
            Create an account
          </h2>
          <p className="mt-2 text-sm text-gray-500">
            Start your 30-day free trial. No credit card required.
          </p>
        </div>

        {/* Form */}
        <form className="space-y-5" onSubmit={handleSignup}>
          
          {/* Name Input */}
          <div>
            <label htmlFor="name" className="block text-sm font-semibold text-gray-700 mb-2">
              Full Name
            </label>
            <input
              id="name"
              type="text"
              placeholder="John Doe"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-gray-50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
              required
            />
          </div>

          {/* Email Input */}
          <div>
            <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="name@company.com"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-gray-50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
              required
            />
          </div>

          {/* Password Input */}
          <div>
            <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="Create a password (min. 8 chars)"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 bg-gray-50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
              required
              minLength={8}
            />
            <p className="mt-1 text-xs text-gray-400">Must be at least 8 characters.</p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200"
          >
            Get started
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or sign up with</span>
          </div>
        </div>

        {/* Social Button */}
        <button
          type="button"
          className="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-200 transition-all duration-200"
        >
          <svg className="h-5 w-5" aria-hidden="true" viewBox="0 0 24 24">
            <path
              d="M12.0003 20.45c4.6667 0 8.0417-3.25 8.0417-8.125 0-0.625-0.0834-1.25-0.2084-1.8333h-7.8333v3.5416h4.5c-0.2083 1.25-1.4167 3.5834-4.5 3.5834-2.7083 0-4.9166-2.2083-4.9166-4.9166s2.2083-4.9167 4.9166-4.9167c1.2917 0 2.4584 0.4583 3.375 1.2917l2.625-2.625c-1.625-1.5417-3.75-2.4583-6-2.4583-4.8333 0-8.75 3.9166-8.75 8.75s3.9167 8.75 8.75 8.75z"
              fill="#4285F4"
            />
          </svg>
          Google
        </button>

        {/* Footer Link */}
        <p className="mt-8 text-center text-sm text-gray-500">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-indigo-600 hover:text-indigo-500 transition-colors">
            Log in
          </Link>
        </p>
      </div>

      {/* RIGHT COLUMN: Visuals */}
      <div className="hidden lg:flex w-1/2 relative bg-gray-900">
        <div className="absolute inset-0 bg-indigo-900/40 mix-blend-multiply z-10" />
        <img
          className="absolute inset-0 h-full w-full object-cover opacity-90"
          src="https://images.unsplash.com/photo-1551434678-e076c223a692?q=80&w=2670&auto=format&fit=crop"
          alt="Office working environment"
        />
        <div className="relative z-20 flex flex-col justify-end h-full p-12 text-white pb-20">
          <h3 className="text-3xl font-bold mb-4">Join our community</h3>
          <p className="text-lg text-indigo-100 max-w-md">
            Get access to the most advanced AI tools and streamline your workflow today.
          </p>
        </div>
      </div>
    </div>
  );
}