"""
I/O Multiplexing Module for ClassChat
select(), poll() and epoll() implementations

"""
import select
import sys


class IOMultiplexer:
    """Handles I/O multiplexing with different methods"""
    
    def __init__(self, method='select'):
        """
        Initialize I/O multiplexer
        
        Args:
            method: 'select', 'poll', or 'epoll'
        """
        self.method = method
        self.poller = None
        
        # Setup based on method
        if method == 'poll' and hasattr(select, 'poll'):
            self.poller = select.poll()
            print(f"[IO] Using poll() for I/O multiplexing")
        elif method == 'epoll' and hasattr(select, 'epoll'):
            self.poller = select.epoll()
            print(f"[IO] Using epoll() for I/O multiplexing")
        else:
            self.method = 'select'
            print(f"[IO] Using select() for I/O multiplexing")
    
    def wait_for_read(self, socket_obj, timeout=1):
        """
        Wait for socket to be readable
        
        Args:
            socket_obj: Socket to monitor
            timeout: Timeout in seconds
            
        Returns:
            True if socket is readable, False otherwise
        """
        if self.method == 'select':
            return self._wait_select(socket_obj, timeout)
        elif self.method == 'poll':
            return self._wait_poll(socket_obj, timeout)
        elif self.method == 'epoll':
            return self._wait_epoll(socket_obj, timeout)
    
    def _wait_select(self, socket_obj, timeout):
        """
        Use select() for I/O multiplexing
        
        Advantages:
        - Cross-platform (Windows, Linux, macOS)
        - Simple to use
        """
        try:
            readable, _, _ = select.select([socket_obj], [], [], timeout)
            return len(readable) > 0
        except Exception as e:
            print(f"[IO ERROR] select() failed: {e}")
            return False
    
    def _wait_poll(self, socket_obj, timeout):
        """
        Use poll() for I/O multiplexing
        
        Advantages:
        - No file descriptor limit
        - Better than select for many connections
        - Available on most Unix systems

        """
        try:
            if not hasattr(select, 'poll'):
                print("[IO] poll() not available, falling back to select()")
                return self._wait_select(socket_obj, timeout)
            
            # Register socket
            poll_obj = select.poll()
            poll_obj.register(socket_obj.fileno(), select.POLLIN)
            
            # Wait for events
            events = poll_obj.poll(timeout * 1000)  # timeout in milliseconds
            
            # Unregister
            poll_obj.unregister(socket_obj.fileno())
            
            return len(events) > 0
            
        except Exception as e:
            print(f"[IO ERROR] poll() failed: {e}")
            return False
    
    def _wait_epoll(self, socket_obj, timeout):
        """
        Use epoll() for I/O multiplexing
        
        Advantages:
        - O(1) complexity for operations
        - Very efficient for large numbers of connections
        - Best performance on Linux
        """
        try:
            if not hasattr(select, 'epoll'):
                print("[IO] epoll() not available, falling back to select()")
                return self._wait_select(socket_obj, timeout)
            
            # Create epoll object
            epoll_obj = select.epoll()
            
            # Register socket for read events
            epoll_obj.register(socket_obj.fileno(), select.EPOLLIN)
            
            # Wait for events
            events = epoll_obj.poll(timeout)
            
            # Cleanup
            epoll_obj.unregister(socket_obj.fileno())
            epoll_obj.close()
            
            return len(events) > 0
            
        except Exception as e:
            print(f"[IO ERROR] epoll() failed: {e}")
            return False
    
    def get_method_info(self):
        """Get information about current I/O method"""
        info = {
            'select': {
                'name': 'select()',
                'complexity': 'O(n)',
                'max_fds': '1024 (typical)',
                'platforms': 'All (Windows, Linux, macOS)',
                'best_for': 'Small number of connections'
            },
            'poll': {
                'name': 'poll()',
                'complexity': 'O(n)',
                'max_fds': 'No limit',
                'platforms': 'Unix/Linux (not Windows)',
                'best_for': 'Moderate number of connections'
            },
            'epoll': {
                'name': 'epoll()',
                'complexity': 'O(1)',
                'max_fds': 'No limit',
                'platforms': 'Linux only',
                'best_for': 'Large number of connections (10,000+)'
            }
        }
        return info.get(self.method, info['select'])



'''
def demonstrate_io_methods():
    """Demonstrate all I/O multiplexing methods"""
    print("=" * 60)
    print("I/O MULTIPLEXING METHODS COMPARISON")
    print("=" * 60)
    print()
    
    methods = ['select', 'poll', 'epoll']
    
    for method in methods:
        multiplexer = IOMultiplexer(method)
        info = multiplexer.get_method_info()
        
        print(f"Method: {info['name']}")
        print(f"  Complexity: {info['complexity']}")
        print(f"  Max FDs: {info['max_fds']}")
        print(f"  Platforms: {info['platforms']}")
        print(f"  Best for: {info['best_for']}")
        print()
    
    print("=" * 60)
    print()
    print("ClassChat uses: " + ("epoll()" if hasattr(select, 'epoll') 
                               else "poll()" if hasattr(select, 'poll')
                               else "select()"))
    print()



if __name__ == "__main__":
    demonstrate_io_methods()

'''