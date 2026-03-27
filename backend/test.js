fetch('http://localhost:3000/api/auth/register', {
  method: 'POST',
  body: JSON.stringify({name: 'test', email: 'test33@test.com', password: 'test'}),
  headers: {'Content-Type': 'application/json'}
}).then(r => r.text()).then(console.log);
