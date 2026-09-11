package task;

//Producer-Consumer Problem
//A shared buffer is used by Producer and Consumer.
//Producer adds items to the buffer and Consumer removes them.
//synchronized, wait() and notifyAll() are used for synchronization.

class SharedBuffer {

 private int[] buffer;       // Array used as the shared buffer
 private int size;           // Maximum size of the buffer

 private int in = 0;         // Position where producer adds the next item
 private int out = 0;        // Position from where consumer removes an item
 private int count = 0;      // Number of items currently in the buffer


 // Constructor to create the buffer
 SharedBuffer(int size) {
     this.size = size;
     buffer = new int[size];
 }


 // Producer method
 // synchronized allows only one thread to access this method at a time
 public synchronized void produce(int value) throws InterruptedException {

     // If buffer is full, producer waits
     while (count == size) {
         wait();
     }

     // Add the item to the buffer
     buffer[in] = value;

     // Move to the next position
     // % size makes the buffer circular
     in = (in + 1) % size;

     // Increase the number of items
     count++;

     System.out.println("Produced: " + value);

     // Notify the waiting consumer
     notifyAll();
 }


 // Consumer method
 public synchronized void consume() throws InterruptedException {

     // If buffer is empty, consumer waits
     while (count == 0) {
         wait();
     }

     // Get the item from the buffer
     int value = buffer[out];

     // Move to the next position
     out = (out + 1) % size;

     // Decrease the number of items
     count--;

     System.out.println("Consumed: " + value);

     // Notify the waiting producer
     notifyAll();
 }
}


//Producer Thread
class Producer extends Thread {

 private SharedBuffer buffer;

 // Constructor
 Producer(SharedBuffer buffer) {
     this.buffer = buffer;
 }

 // run() method is executed when thread starts
 public void run() {

     // Produce numbers from 1 to 10
     for (int i = 1; i <= 10; i++) {

         try {
             buffer.produce(i);

             // Small delay after producing
             Thread.sleep(300);
         }

         catch (InterruptedException e) {
             Thread.currentThread().interrupt();
             break;
         }
     }
 }
}


//Consumer Thread
class Consumer extends Thread {

 private SharedBuffer buffer;

 // Constructor
 Consumer(SharedBuffer buffer) {
     this.buffer = buffer;
 }

 // run() method is executed when thread starts
 public void run() {

     // Consume 10 items
     for (int i = 1; i <= 10; i++) {

         try {
             buffer.consume();

             // Small delay after consuming
             Thread.sleep(500);
         }

         catch (InterruptedException e) {
             Thread.currentThread().interrupt();
             break;
         }
     }
 }
}
package task;

public class ProducerConsumer {

	 public static void main(String[] args) {

	     // Create a shared buffer with capacity 5
	     SharedBuffer buffer = new SharedBuffer(5);

	     // Create Producer and Consumer threads
	     Producer producer = new Producer(buffer);
	     Consumer consumer = new Consumer(buffer);

	     // Start both threads
	     producer.start();
	     consumer.start();
	 }
	}
