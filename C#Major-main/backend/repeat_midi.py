
import sys
import mido

input_file = sys.argv[1] if len(sys.argv) > 1 else "two_second_loop.mid"
output_file = sys.argv[2] if len(sys.argv) > 2 else "two_second_loop_20s.mid"
repeats = 10

original = mido.MidiFile(input_file)

# Find the phrase length in MIDI ticks across all tracks.
loop_ticks = max(sum(msg.time for msg in track) for track in original.tracks)

repeated = mido.MidiFile(
    type=original.type,
    ticks_per_beat=original.ticks_per_beat
)

for track in original.tracks:
    new_track = mido.MidiTrack()
    repeated.tracks.append(new_track)

    # Convert original delta times into absolute times.
    absolute_events = []
    tick = 0

    for msg in track:
        tick += msg.time
        if msg.type != "end_of_track":
            absolute_events.append((tick, msg))

    # Repeat the events at each phrase boundary.
    repeated_events = []

    for i in range(repeats):
        offset = i * loop_ticks
        for event_tick, msg in absolute_events:
            repeated_events.append((offset + event_tick, msg))

    repeated_events.sort(key=lambda item: item[0])

    # Convert absolute times back to MIDI delta times.
    previous_tick = 0

    for event_tick, msg in repeated_events:
        new_track.append(msg.copy(time=event_tick - previous_tick))
        previous_tick = event_tick

    new_track.append(
        mido.MetaMessage(
            "end_of_track",
            time=max(0, loop_ticks * repeats - previous_tick)
        )
    )

repeated.save(output_file)

print(f"Saved: {output_file}")
print(f"Phrase repetitions: {repeats}")
print(f"Target duration: 20 seconds at 120 BPM")
print(f"MIDI ticks per phrase: {loop_ticks}")
