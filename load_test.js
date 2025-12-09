import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 1000 },   // ramp up to 1000
    { duration: '40s', target: 1000 },   // ramp up to 3000
    { duration: '50s', target: 1000 },   // ramp up to 5000
    { duration: '1m', target: 1000 },    // stay at peak (heavy stress)
    { duration: '30s', target: 0 },      // ramp down
  ],
};

export default function () {
  http.get('http://127.0.0.1:8000/');  // <-- Replace this with your website link
  sleep(1);
}
