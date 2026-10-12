const fs = require('fs');
const content = fs.readFileSync('C:\\\\Projects\\\\dav-agri\\\\frontend\\\\src\\\\screens\\\\LoginScreen.tsx', 'utf8');

const oldFunc = \  const handleDemoSignIn = () => {
    completeSignIn('google_token_mock_farmer');
  };\;

const newFunc = \  // Honest demo entry: the seeded dev farmer logs in with a real username
  // (their phone number, which is what a farmer actually remembers) and the
  // seeded dev password. This is NOT masked as Google authentication.
  const handleDemoSignIn = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await authService.login('9876543210', 'password123');
      const user = await authService.getCurrentUser();
      store.setUser(user);
      store.routeAfterAuth({ onboarding_completed: res.onboarding_completed ?? user.onboarding_completed });
    } catch (err: any) {
      setError(err.message || t.login_failed);
    } finally {
      setLoading(false);
    }
  };\;

let newContent = content.replace(oldFunc, newFunc);
newContent = newContent.replace('{loading ? t.connecting : t.demo_sign_in}', '{t.demo_farmer}');

fs.writeFileSync('C:\\\\Projects\\\\dav-agri\\\\frontend\\\\src\\\\screens\\\\LoginScreen.tsx', newContent);
console.log('LoginScreen.tsx updated successfully');
