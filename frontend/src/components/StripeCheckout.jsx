import { useState } from 'react'
import api from '../utils/api'

export default function RazorpayCheckout({ bookingId, amount, userName, userEmail, onSuccess, onCancel }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePayment = async () => {
    setError(null)
    setLoading(true)

    try {
      // Step 1: Create Razorpay Order
      const orderRes = await api.post('/payments/create-order/', {
        booking_id: bookingId
      })

      const { razorpay_order_id, payment_id, razorpay_key_id } = orderRes.data

      // Step 2: Open Razorpay Checkout
      const options = {
        key: razorpay_key_id,
        amount: Math.round(amount * 100), // Amount in paise
        currency: 'INR',
        name: 'Sessions Marketplace',
        description: 'Session Booking Payment',
        order_id: razorpay_order_id,
        prefill: {
          name: userName,
          email: userEmail
        },
        handler: async (response) => {
          try {
            // Step 3: Verify payment on backend
            await api.post('/payments/verify/', {
              payment_id,
              razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature
            })

            if (onSuccess) {
              onSuccess(response)
            }
          } catch (err) {
            setError(err.response?.data?.error || 'Payment verification failed')
          } finally {
            setLoading(false)
          }
        },
        modal: {
          ondismiss: () => {
            setLoading(false)
            setError('Payment cancelled')
          }
        },
        theme: {
          color: '#3399cc'
        }
      }

      // Load Razorpay script if not already loaded
      if (!window.Razorpay) {
        const script = document.createElement('script')
        script.src = 'https://checkout.razorpay.com/v1/checkout.js'
        script.onload = () => {
          const rzp = new window.Razorpay(options)
          rzp.open()
        }
        document.body.appendChild(script)
      } else {
        const rzp = new window.Razorpay(options)
        rzp.open()
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create order')
      setLoading(false)
    }
  }

  return (
    <div className="razorpay-checkout">
      <h3>Complete Payment</h3>
      <p>Amount: ₹{amount}</p>

      {error && <p className="error">{error}</p>}

      <div className="form-actions">
        <button 
          onClick={handlePayment}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Processing...' : `Pay ₹${amount}`}
        </button>
        {onCancel && (
          <button 
            onClick={onCancel}
            disabled={loading}
            className="btn-secondary"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  )
}
