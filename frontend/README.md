# LUMI Mobile (Expo)

This is a starter React Native (Expo) frontend for the LUMI backend.

## Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Run the app:

```bash
npm start
```

Then open on a simulator or device using the Expo Go app.

## Notes
- The app expects the backend to be running at `http://10.0.2.2:5000/api`. If you are testing on a physical device, update `src/api.js` to point to your machine's local IP.
- The app currently supports login/register, viewing/updating profile, and basic navigation scaffold.

## Next steps
- Add camera + image upload screens for vision and payments
- Add voice recording + upload for transcription
- Add UI for `audio_message` playback (TTS) using `expo-av`
- Add token refresh handling (refresh token endpoint)
