package main

import (
	"context"
	"testing"
	"time"
)

func TestTouchWakesIdleFrame(t *testing.T) {
	d := &differ{still: 12, wake: make(chan struct{}, 1)}
	done := make(chan bool, 1)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	go func() { done <- d.wait(ctx, false) }()
	select {
	case <-done:
		t.Fatal("idle frame did not wait")
	case <-time.After(30 * time.Millisecond):
	}
	d.interact()
	select {
	case ok := <-done:
		if !ok {
			t.Fatal("touch cancelled the frame")
		}
	case <-time.After(150 * time.Millisecond):
		t.Fatal("touch remained behind the idle delay")
	}
	if delay := d.pace(false); delay > 40*time.Millisecond {
		t.Fatal("gesture returned to idle pacing")
	}
}

func TestFrameWaitStopsWhenDisconnected(t *testing.T) {
	d := &differ{still: 12, wake: make(chan struct{}, 1)}
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan bool, 1)
	go func() { done <- d.wait(ctx, false) }()
	cancel()
	select {
	case ok := <-done:
		if ok {
			t.Fatal("disconnected frame should not be acknowledged")
		}
	case <-time.After(150 * time.Millisecond):
		t.Fatal("disconnect remained behind the idle delay")
	}
}
